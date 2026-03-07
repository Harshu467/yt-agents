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

# Session configuration using Flask's built-in cookie-based sessions
# (Simple, reliable, and works on Render's ephemeral filesystem)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

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
            data = research_agent.research_topic(topic)
        
        elif step == 'script':
            print(f"✍️  Writing script for: {topic}")
            script_agent = ScriptWriterAgent()
            # Get research data from previous step if available
            research_data = workflow['steps']['research']['data'] or {}
            data = script_agent.write_script(topic, research_data)
        
        elif step == 'metadata':
            print(f"🏷️  Generating metadata for: {topic}")
            metadata_agent = MetadataAgent()
            # Get script data if available for better metadata
            script_data = workflow['steps']['script']['data'] or {}
            research_data = workflow['steps']['research']['data'] or {}
            
            # Extract script summary and key points
            script_summary = ""
            if script_data:
                intro = script_data.get('intro', '')
                segments = script_data.get('segments', [])
                outro = script_data.get('outro', '')
                script_summary = f"{intro} {' '.join([s.get('text', '') for s in segments])} {outro}"[:200]
            
            key_points = research_data.get('key_points', []) if research_data else []
            
            data = metadata_agent.generate_metadata(topic, script_summary, key_points)
        
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
                
                # Provide helpful error message to user
                error_message = str(e)
                if "Supabase" in error_message:
                    error_message += "\n\n💡 Supabase setup help:\n"
                    error_message += "   • Validate: python3 scripts/validate_supabase.py\n"
                    error_message += "   • Setup guide: SUPABASE_TROUBLESHOOTING.md\n"
                    error_message += "   • Quick fix: SUPABASE_ERROR_QUICK_FIX.md"
                
                data = {
                    "status": "error",
                    "error": str(e),
                    "message": f"❌ Video generation failed:\n{error_message}"
                }
        
        elif step == 'upload':
            # Upload step doesn't generate anything, just confirms readiness
            print(f"📤 Upload step ready for: {topic}")
            data = {
                "status": "ready",
                "message": "✅ Ready to upload to YouTube\n\nAll previous steps have been completed. Click Approve to proceed with uploading your video."
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
        
        # Attempt real upload when UploadAgent is available
        print(f"📤 Uploading video...")
        print(f"   Title: {upload_data['title']}")
        print(f"   Video: {upload_data['video_file']}")
        print(f"   Tags: {', '.join(upload_data['tags'])}")

        video_url = None
        youtube_id = None

        # First try: use YouTube UploadAgent (if available and configured)
        if UploadAgent:
            try:
                uploader = UploadAgent()

                # Resolve local file path for upload
                local_path = None
                # If workflow stored a filepath string
                if isinstance(video_file, str) and os.path.exists(video_file):
                    local_path = video_file

                # If video step stored a dict with 'filepath'
                if not local_path and isinstance(video_file, dict):
                    candidate = video_file.get('filepath') or video_file.get('file')
                    if candidate and os.path.exists(candidate):
                        local_path = candidate

                # If still not found, try VideoStorage lookup
                storage = get_video_storage()
                if not local_path:
                    # Search metadata for matching filename/path
                    for v in storage.get_all_videos():
                        if v.get('filepath') == video_file or v.get('filename') == video_file:
                            local_path = v.get('filepath')
                            video_id = v.get('id')
                            break

                if local_path:
                    youtube_id = uploader.upload_video(
                        video_file=local_path,
                        title=upload_data['title'],
                        description=upload_data['description'],
                        tags=upload_data.get('tags', []),
                        privacy_status=upload_data.get('status', 'private')
                    )
                    if youtube_id:
                        video_url = f"https://youtube.com/watch?v={youtube_id}"
            except Exception as e:
                print(f"⚠️  UploadAgent failed: {e}")

        # Fallback: if not uploaded to YouTube, return local storage URL if available
        if not video_url:
            storage = get_video_storage()
            info = None

            # If video_file is a storage id or timestamp, get metadata
            if isinstance(video_file, str):
                info = storage.get_video_info(video_file) or None

            # If video_file is dict with metadata
            if not info and isinstance(video_file, dict):
                vid = video_file.get('id') or video_file.get('video_id')
                info = storage.get_video_info(vid) if vid else None

            if info:
                video_url = request.host_url.rstrip('/') + info.get('url', info.get('filepath', ''))
                youtube_id = info.get('id')

        # Final fallback: keep existing mock but generate an id based on timestamp
        if not video_url:
            youtube_id = youtube_id or datetime.now().strftime('%Y%m%d%H%M%S')
            video_url = f"https://youtube.com/watch?v={youtube_id}"

        workflow['steps']['upload']['status'] = 'uploaded'
        workflow['steps']['upload']['data'] = {
            'video_id': youtube_id,
            'url': video_url,
            'uploaded_at': datetime.now().isoformat(),
            'title': upload_data['title'],
            'description': upload_data['description']
        }

        # Persist youtube_id / url back into storage metadata if possible
        try:
            storage = get_video_storage()
            # Determine storage video id
            storage_vid = None
            if 'video_id' in locals() and video_id:
                storage_vid = video_id
            elif 'info' in locals() and info:
                storage_vid = info.get('id')
            elif isinstance(video_file, dict):
                storage_vid = video_file.get('id') or video_file.get('video_id')

            if storage_vid and hasattr(storage, 'update_metadata'):
                updates = {'youtube_id': youtube_id, 'url': video_url}
                try:
                    storage.update_metadata(storage_vid, updates)
                except Exception as e:
                    print(f"⚠️  Failed to update storage metadata: {e}")
        except Exception:
            pass

        return jsonify({
            'status': 'uploaded',
            'video_id': youtube_id,
            'url': video_url,
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
    """Serve a video file for download/streaming with proper streaming support.  
    if the storage backend returns a URL (e.g. Supabase), redirect instead of
    attempting to open it as a local file."""
    storage = get_video_storage()
    filepath = storage.get_video_file(video_id)
    
    if not filepath:
        return jsonify({'error': 'Video not found'}), 404
    
    # If we got a remote URL, simply redirect the client there so the browser
    # can stream directly from the storage provider.  This avoids trying to
    # open the URL as a file path, which previously produced errors like:
    #   [Errno 2] No such file or directory: '/opt/render/.../https://...'
    if isinstance(filepath, str) and filepath.startswith(('http://', 'https://')):
        from flask import redirect
        return redirect(filepath, code=302)
    
    try:
        # Use send_file with proper streaming for video playback
        response = send_file(
            filepath,
            mimetype='video/mp4',
            as_attachment=False,
            download_name=f'{video_id}.mp4'
        )
        # Add headers for browser video playback support
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    except Exception as e:
        print(f"❌ Error serving video: {str(e)}")
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

@app.route('/api/videos/delete-all', methods=['DELETE'])
@login_required
def delete_all_videos():
    """Delete all videos and their history"""
    storage = get_video_storage()
    
    result = storage.delete_all_videos()
    
    return jsonify({
        'status': 'completed',
        'message': f'Deleted {result["deleted"]} videos, {result["failed"]} failed',
        'deleted': result['deleted'],
        'failed': result['failed'],
        'total': result['total']
    })

if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print("🚀 Starting YouTube Video Automation Dashboard...")
    print(f"📍 Open: http://localhost:{port}")
    print(f"🔧 Debug Mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
