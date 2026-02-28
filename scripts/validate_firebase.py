#!/usr/bin/env python3
"""Validate Firebase Storage and Firestore configuration."""
import sys
import os
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

def validate_firebase():
    """Check Firebase credentials and connectivity."""
    
    print("🔍 Validating Firebase setup...\n")
    
    # Check env vars
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
    
    if not creds_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Set it to the path of your service account JSON file")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Service account file not found: {creds_path}")
        return False
    
    print(f"✅ Service account file found: {creds_path}")
    
    if not bucket:
        print("❌ FIREBASE_STORAGE_BUCKET not set")
        print("   Set it to your Firebase project (e.g., my-project.appspot.com)")
        return False
    
    print(f"✅ Firebase bucket configured: {bucket}")
    
    # Try to initialize Firebase clients
    try:
        from google.cloud import storage as gcs
        from google.cloud import firestore
        print("✅ Google Cloud libraries installed\n")
    except ImportError as e:
        print(f"❌ Missing Google Cloud library: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    try:
        fs = firestore.Client()
        print("✅ Firestore initialized")
        
        # Try to list collections (basic connectivity check)
        collections = list(fs.collections())
        print(f"   Collections found: {len(collections)}")
        for col in collections[:3]:
            print(f"     - {col.id}")
        
    except Exception as e:
        print(f"❌ Firestore error: {e}")
        print("   Check that Firestore is enabled in Firebase Console")
        return False
    
    try:
        gcs_client = gcs.Client()
        bucket_obj = gcs_client.bucket(bucket)
        
        # Check if bucket exists
        if not bucket_obj.exists():
            print(f"❌ Storage bucket does not exist: {bucket}")
            return False
        
        print("✅ Cloud Storage bucket accessible")
        
        # List blobs (if any)
        blobs = list(bucket_obj.list_blobs(max_results=5))
        print(f"   Files in bucket: {len(blobs)}")
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        print("   Check that Cloud Storage is enabled in Firebase Console")
        return False
    
    print("\n✅ All Firebase services are correctly configured!")
    return True


if __name__ == '__main__':
    success = validate_firebase()
    sys.exit(0 if success else 1)
