#!/usr/bin/env python3
"""
Simple script to check if the backend deployment is working
"""
import requests
import time

def check_deployment():
    backend_url = "https://max-betting-ai.onrender.com"
    
    print(f"🚀 Checking backend deployment at: {backend_url}")
    print("=" * 60)
    
    # Check health endpoint
    try:
        print("Checking /health endpoint...")
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
    
    # Check root endpoint
    try:
        print("\nChecking root endpoint...")
        response = requests.get(backend_url, timeout=10, allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 302, 307]:
            print("✅ Root endpoint is responding!")
        else:
            print(f"❌ Root endpoint returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Check docs endpoint
    try:
        print("\nChecking /docs endpoint...")
        response = requests.get(f"{backend_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API docs are available!")
        else:
            print(f"❌ API docs failed with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API docs failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"🌐 Your backend URL: {backend_url}")
    print(f"📚 API Documentation: {backend_url}/docs")
    print(f"🔗 Frontend URL: https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app")

if __name__ == "__main__":
    check_deployment()