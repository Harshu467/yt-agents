"""
YouTube Video Automation Dashboard - Flask Web Application
Step-by-step workflow: Topic → Research → Script → Metadata → Video → Upload
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pathlib import Path
import json
import os
from datetime import datetime
import uuid

# Import agents
from agents.trend_detector import TrendDetectorAgent
from agents.research_agent import ResearchAgent
from agents.script_writer import ScriptWriterAgent
from agents.metadata_agent import MetadataAgent
from agents.upload_agent import UploadAgent
from config import Config

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Storage for workflow sessions
WORKFLOWS = {}

@app.route('/')
def index():
    """Home page - start new workflow"""
    return render_template('index.html')

@app.route('/start-workflow', methods=['POST'])
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
def workflow_dashboard(workflow_id):
    """Main workflow dashboard"""
    if workflow_id not in WORKFLOWS:
        return redirect(url_for('index'))
    
    workflow = WORKFLOWS[workflow_id]
    return render_template('workflow.html', workflow=workflow)

@app.route('/api/workflow/<workflow_id>/step/<step>', methods=['GET', 'POST'])
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
            data = {
                "status": "ready",
                "resolution": "1280x720",
                "duration": "10 minutes",
                "file": "video_output.mp4"
            }
        
        elif step == 'upload':
            # Handle upload
            upload_data = request.json.get('upload_data', {})
            print(f"📤 Uploading video: {upload_data}")
            return jsonify({'status': 'success', 'message': 'Video uploaded!'})
        
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
def reject_step(workflow_id, step):
    """Reject a workflow step"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    workflow['steps'][step]['status'] = 'rejected'
    
    return jsonify({'status': 'rejected'})

@app.route('/api/workflow/<workflow_id>/upload', methods=['POST'])
def final_upload(workflow_id):
    """Final upload to YouTube"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    
    try:
        # Check if all steps are approved
        for step in ['research', 'script', 'metadata', 'video']:
            if workflow['steps'][step]['status'] != 'approved':
                return jsonify({'error': f'Step {step} not approved'}), 400
        
        # Prepare upload data
        upload_data = {
            'title': workflow['steps']['metadata']['data']['title'],
            'description': workflow['steps']['metadata']['data']['description'],
            'tags': workflow['steps']['metadata']['data']['tags'],
            'video_file': workflow['steps']['video']['data']['file']
        }
        
        # Simulate upload
        print(f"📤 Uploading video to YouTube...")
        print(f"   Title: {upload_data['title']}")
        print(f"   Video: {upload_data['video_file']}")
        
        workflow['steps']['upload']['status'] = 'uploaded'
        workflow['steps']['upload']['data'] = {
            'video_id': 'dQw4w9WgXcQ',  # Mock YouTube video ID
            'url': 'https://youtube.com/watch?v=dQw4w9WgXcQ',
            'uploaded_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'uploaded',
            'video_id': 'dQw4w9WgXcQ',
            'message': 'Video uploaded successfully!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/<workflow_id>/summary', methods=['GET'])
def workflow_summary(workflow_id):
    """Get complete workflow summary"""
    if workflow_id not in WORKFLOWS:
        return jsonify({'error': 'Workflow not found'}), 404
    
    workflow = WORKFLOWS[workflow_id]
    return jsonify(workflow)

if __name__ == '__main__':
    print("🚀 Starting YouTube Video Automation Dashboard...")
    print("📍 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
