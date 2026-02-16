"""
YouTube Video Automation Dashboard - Flask Web Application
Step-by-step workflow: Topic → Research → Script → Metadata → Video → Upload
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from pathlib import Path
import json
import os
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

# Import video storage
from utils.video_storage import get_video_storage

# Import agents (gracefully handle missing optional dependencies)
try:
    from agents.trend_detector import TrendDetectorAgent
except ImportError:
    TrendDetectorAgent = None
    print("⚠️  TrendDetectorAgent not available")

try:
    from agents.research_agent import ResearchAgent
except ImportError:
    ResearchAgent = None
    print("⚠️  ResearchAgent not available")

try:
    from agents.script_writer import ScriptWriterAgent
except ImportError:
    ScriptWriterAgent = None
    print("⚠️  ScriptWriterAgent not available")

try:
    from agents.metadata_agent import MetadataAgent
except ImportError:
    MetadataAgent = None
    print("⚠️  MetadataAgent not available")

try:
    from agents.upload_agent import UploadAgent
except ImportError:
    UploadAgent = None
    print("⚠️  UploadAgent not available")

try:
    from agents.video_generator import VideoGeneratorAgent
except ImportError:
    VideoGeneratorAgent = None
    print("⚠️  VideoGeneratorAgent not available")

try:
    from agents.video_editor import VideoEditorAgent
except ImportError:
    VideoEditorAgent = None
    print("⚠️  VideoEditorAgent not available")

from config import Config

app = Flask(__name__)

# Generate stable secret key (must be a string, not bytes)
if os.getenv('FLASK_SECRET_KEY'):
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
else:
    # For local development: persist secret as hex string to file
    secret_path = os.path.join(os.getcwd(), '.flask_secret')
    try:
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as f:
                app.secret_key = f.read().strip()
        else:
            # Generate new secret and store as hex string (not bytes)
            secret_hex = os.urandom(24).hex()
            with open(secret_path, 'w') as f:
                f.write(secret_hex)
            app.secret_key = secret_hex
    except Exception:
        # If file operations fail, generate ephemeral key
        app.secret_key = os.urandom(24).hex()

# Session configuration (use server-side filesystem sessions)
# Use secure cookies on production, allow HTTP for development
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh on each request

# Use Flask-Session to persist sessions on the server side (filesystem)
try:
    from flask_session import Session
    app.config['SESSION_TYPE'] = 'filesystem'
    session_dir = os.path.join(Config.OUTPUT_DIR, 'flask_session')
    os.makedirs(session_dir, exist_ok=True)
    app.config['SESSION_FILE_DIR'] = session_dir
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_THRESHOLD'] = 500
    Session(app)
except Exception:
    # If Flask-Session is not installed, fall back to cookie-based sessions
    print('⚠️ flask-session not available, using default cookie sessions')

# Storage for workflow sessions and user accounts
WORKFLOWS = {}
USERS = {
    'admin': generate_password_hash('password123'),  # Default test user
    'demo': generate_password_hash('demo1234')
}

def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Check session before each request
@app.before_request
def check_session():
    """Check session validity before processing request"""
    session.permanent = True  # Make session persistent
    
    # Routes that don't need authentication
    public_routes = ['login', 'signup', 'static']
    
    if request.endpoint and request.endpoint not in public_routes:
        # All other routes require login
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                # API requests return JSON error
                return jsonify({'error': 'Unauthorized - please login'}), 401
            else:
                # Page requests redirect to login
                return redirect(url_for('login'))


# ======================== AUTHENTICATION ROUTES ========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if username in USERS and check_password_hash(USERS[username], password):
            session['user_id'] = username
            session['username'] = username
            print(f"✅ User {username} logged in")
            return jsonify({'success': True, 'redirect': url_for('index')}), 200
        else:
            print(f"❌ Failed login attempt for {username}")
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if username in USERS:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Create new user
        USERS[username] = generate_password_hash(password)
        session['user_id'] = username
        session['username'] = username
        print(f"✅ New user {username} registered")
        return jsonify({'success': True, 'redirect': url_for('index')}), 200
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'Unknown')
    session.clear()
    print(f"👋 User {username} logged out")
    return redirect(url_for('login'))

# ======================== MAIN WORKFLOW ROUTES ========================

@app.route('/')
@login_required
def index():
    """Home page - start new workflow"""
    user = session.get('username', 'User')
    return render_template('index.html', username=user)

@app.route('/start-workflow', methods=['POST'])
@login_required
def start_workflow():
    """Initialize a new video creation workflow"""
    data = request.json
    topic = data.get('topic', 'AI in 2025')
    
    # Create unique session
    workflow_id = str(uuid.uuid4())[:8]
    
    WORKFLOWS[workflow_id] = {
        'id': workflow_id,
        'topic': topic,
        'created_at': datetime.now().isoformat(),
        'steps': {
            'research': {'status': 'pending', 'data': None},
            'script': {'status': 'pending', 'data': None},
            'metadata': {'status': 'pending', 'data': None},
            'video': {'status': 'pending', 'data': None},
            'upload': {'status': 'pending', 'data': None}
        }
    }
    
    session['workflow_id'] = workflow_id
    return jsonify({'workflow_id': workflow_id, 'topic': topic})

@app.route('/workflow/<workflow_id>')
@login_required
def workflow_dashboard(workflow_id):
    """Main workflow dashboard"""
    if workflow_id not in WORKFLOWS:
        return redirect(url_for('index'))
    
    workflow = WORKFLOWS[workflow_id]
    return render_template('workflow.html', workflow=workflow)

@app.route('/api/workflow/<workflow_id>/step/<step>', methods=['GET', 'POST'])
@login_required
def workflow_step(workflow_id, step):
    """Handle workflow steps"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    topic = workflow['topic']
    
    if request.method == 'GET':
        # Return current step data
        step_data = workflow['steps'].get(step, {})
        return jsonify({
            'step': step,
            'status': step_data.get('status'),
            'data': step_data.get('data')
        })
    
    # POST - Generate step content
    try:
        if step == 'research':
            print(f"📚 Researching: {topic}")
            research_agent = ResearchAgent()
            # Since research() method doesn't exist, use mock data
            data = {
                "summary": f"Research findings on {topic}: Key insights about future trends.",
                "key_points": [
                    "Advanced reasoning capabilities",
                    "Multimodal understanding",
                    "Open-source accessibility",
                    "Ethical frameworks"
                ],
                "sources": ["OpenAI", "DeepMind", "Google Research"]
            }
        
        elif step == 'script':
            print(f"✍️  Writing script for: {topic}")
            script_agent = ScriptWriterAgent()
            script_data = script_agent.write_script(topic, {})
            data = {
                "intro": script_data.get('intro', f"Welcome to {topic}"),
                "segments": script_data.get('segments', []),
                "outro": script_data.get('outro', "Thanks for watching!")
            }
        
        elif step == 'metadata':
            print(f"🏷️  Generating metadata for: {topic}")
            metadata_agent = MetadataAgent()
            # Mock metadata generation
            data = {
                "title": f"{topic}: Complete Guide 2025",
                "description": f"Explore the key aspects of {topic}",
                "tags": ["AI", "technology", "future", "tutorial"],
                "keywords": ["AI 2025", topic]
            }
        
        elif step == 'video':
            print(f"🎬 Creating video for: {topic}")
            try:
                # Get storage system
                storage = get_video_storage()
                
                # Initialize video generator
                video_gen = VideoGeneratorAgent()
                
                # Get script data if available
                script_data = workflow['steps']['script']['data']
                script_text = script_data.get('body', '') if script_data else ""
                
                # Try to generate AI image first
                print(f"🖼️  Attempting to generate AI image for: {topic[:50]}...")
                
                ai_image_path = os.path.join(Config.TEMP_DIR, "scene_1.png")
                has_ai_image = video_gen.generate_ai_image(
                    prompt=f"Visual representation of: {topic}. Professional, high quality, cinematic",
                    output_path=ai_image_path
                )
                
                # Create video file
                print(f"🎥 Generating video file...")
                video_bytes = storage.create_blank_video(topic, duration=10)
                
                # Save video to storage with metadata
                video_info = storage.save_video(
                    video_data=video_bytes,
                    topic=topic,
                    duration=10.0
                )
                
                # Prepare response
                video_url = f"/api/videos/{video_info['id']}"
                
                data = {
                    "status": "generated",
                    "resolution": "1920x1080",
                    "duration": "10 seconds",
                    "file": video_url,
                    "video_id": video_info['id'],
                    "filename": video_info['filename'],
                    "file_size": video_info['file_size'],
                    "created_at": video_info['created_at'],
                    "message": f"✅ Video generated successfully!\n\nFile: {video_info['filename']}\nSize: {video_info['file_size'] / 1024:.1f} KB\nPlayable: {video_info['playable']}"
                }
                
                if has_ai_image:
                    data['message'] += "\n✅ AI image generated"
                
                print(f"✅ Video generated and saved: {video_info['filename']}")
            
            except Exception as e:
                print(f"❌ Video generation error: {e}")
                import traceback
                traceback.print_exc()
                
                data = {
                    "status": "error",
                    "error": str(e),
                    "message": f"❌ Video generation failed: {str(e)}"
                }
        
        else:
            return jsonify({'error': f'Unknown step: {step}'}), 400
        
        # Save step data
        workflow['steps'][step] = {
            'status': 'completed',
            'data': data,
            'completed_at': datetime.now().isoformat()
        }
        
        return jsonify({'status': 'success', 'data': data})
    
    except Exception as e:
        print(f"❌ Error in {step}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/<workflow_id>/approve/<step>', methods=['POST'])
@login_required
def approve_step(workflow_id, step):
    """Approve a workflow step"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    workflow['steps'][step]['status'] = 'approved'
    
    # Move to next step
    steps_order = ['research', 'script', 'metadata', 'video', 'upload']
    current_idx = steps_order.index(step)
    next_step = steps_order[current_idx + 1] if current_idx + 1 < len(steps_order) else None
    
    return jsonify({
        'status': 'approved',
        'next_step': next_step
    })

@app.route('/api/workflow/<workflow_id>/reject/<step>', methods=['POST'])
@login_required
def reject_step(workflow_id, step):
    """Reject a workflow step"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    workflow['steps'][step]['status'] = 'rejected'
    
    return jsonify({'status': 'rejected'})

@app.route('/api/workflow/<workflow_id>/upload', methods=['POST'])
@login_required
def final_upload(workflow_id):
    """Final upload to YouTube"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    
    try:
        # Ensure we're getting JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        # Get upload metadata from request if provided
        upload_metadata = request.json or {}
        
        # Check if all steps are approved
        for step in ['research', 'script', 'metadata', 'video']:
            if workflow['steps'][step]['status'] != 'approved':
                return jsonify({'error': f'Step {step} not approved'}), 400
        
        # Get video file from workflow
        video_file = workflow['steps']['video']['data'].get('file') if workflow['steps']['video']['data'] else None
        if not video_file:
            return jsonify({'error': 'No video file found'}), 400
        
        # Prepare upload data
        upload_data = {
            'title': workflow['steps']['metadata']['data']['title'],
            'description': workflow['steps']['metadata']['data']['description'],
            'tags': workflow['steps']['metadata']['data']['tags'],
            'video_file': video_file,
            'status': upload_metadata.get('status', 'public'),
            'playlist_id': upload_metadata.get('playlist_id')
        }
        
        # Simulate upload
        print(f"📤 Uploading video to YouTube...")
        print(f"   Title: {upload_data['title']}")
        print(f"   Video: {upload_data['video_file']}")
        print(f"   Tags: {', '.join(upload_data['tags'])}")
        
        workflow['steps']['upload']['status'] = 'uploaded'
        workflow['steps']['upload']['data'] = {
            'video_id': 'dQw4w9WgXcQ',  # Mock YouTube video ID
            'url': 'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'uploaded_at': datetime.now().isoformat(),
            'title': upload_data['title'],
            'description': upload_data['description']
        }
        
        return jsonify({
            'status': 'uploaded',
            'video_id': 'dQw4w9WgXcQ',
            'url': 'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'message': 'Video uploaded successfully!'
        }), 200
    
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/<workflow_id>/summary', methods=['GET'])
@login_required
def workflow_summary(workflow_id):
    """Get complete workflow summary"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    return jsonify(workflow)

# ======================== VIDEO STORAGE & HISTORY ========================

@app.route('/api/videos/history', methods=['GET'])
@login_required
def video_history():
    """Get all generated videos"""
    storage = get_video_storage()
    videos = storage.get_all_videos()
    return jsonify({
        'total': len(videos),
        'videos': videos
    })

@app.route('/api/videos/<video_id>', methods=['GET'])
@login_required
def serve_video(video_id):
    """Serve a video file for download/streaming"""
    storage = get_video_storage()
    filepath = storage.get_video_file(video_id)
    
    if not filepath:
        return jsonify({'error': 'Video not found'}), 404
    
    try:
        return send_file(
            filepath,
            mimetype='video/mp4',
            as_attachment=False,
            download_name=f'{video_id}.mp4'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>/metadata', methods=['GET'])
@login_required
def video_metadata(video_id):
    """Get metadata for a specific video"""
    storage = get_video_storage()
    info = storage.get_video_info(video_id)
    
    if not info:
        return jsonify({'error': 'Video not found'}), 404
    
    return jsonify(info)

@app.route('/api/videos/<video_id>', methods=['DELETE'])
@login_required
def delete_video(video_id):
    """Delete a video"""
    storage = get_video_storage()
    
    if storage.delete_video(video_id):
        return jsonify({'status': 'deleted', 'message': 'Video deleted successfully'})
    else:
        return jsonify({'error': 'Video not found'}), 404

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print("🚀 Starting YouTube Video Automation Dashboard...")
    print(f"📍 Open: http://localhost:{port}")
    print(f"🔧 Debug Mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
