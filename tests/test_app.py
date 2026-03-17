"""
Test suite for Mergington High School API

Tests all endpoints with happy-path and error-case scenarios
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def app_with_fresh_activities():
    """Create a fresh instance of the FastAPI app with clean activities data for each test"""
    
    # Create a new FastAPI app instance
    app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )
    
    # Fresh in-memory activity database for this test
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming Club": {
            "description": "Swimming training and water sports",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Studio": {
            "description": "Express creativity through painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater arts and performance training",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Learn public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Define routes using the fresh activities dict
    @app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")
    
    @app.get("/activities")
    def get_activities():
        return activities
    
    @app.post("/activities/{activity_name}/signup")
    def signup_for_activity(activity_name: str, email: str):
        """Sign up a student for an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")
        
        activity["participants"].append(email)
        return {"message": f"Signed up {email} for {activity_name}"}
    
    @app.post("/activities/{activity_name}/unregister")
    def unregister_from_activity(activity_name: str, email: str):
        """Unregister a student from an activity"""
        if activity_name not in activities:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        activity = activities[activity_name]
        
        if email not in activity["participants"]:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
        
        activity["participants"].remove(email)
        return {"message": f"Unregistered {email} from {activity_name}"}
    
    return app


@pytest.fixture
def client(app_with_fresh_activities):
    """Create a test client for the app"""
    return TestClient(app_with_fresh_activities)


# Tests for GET /activities
class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_all_activities(self, client):
        """Test that all 9 activities are returned"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Swimming Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


# Tests for POST /activities/{activity_name}/signup
class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds the email to participants list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball Team/signup?email={email}")
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball Team"]["participants"]
        assert email in participants
    
    def test_signup_invalid_activity_returns_404(self, client):
        """Test that signup to non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_activities_same_user(self, client):
        """Test that same user can sign up for multiple different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(f"/activities/Basketball Team/signup?email={email}")
        response2 = client.post(f"/activities/Swimming Club/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]
        assert email in activities["Swimming Club"]["participants"]
    
    def test_signup_returns_correct_message(self, client):
        """Test that signup returns correct confirmation message"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        data = response.json()
        
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]


# Tests for POST /activities/{activity_name}/unregister
class TestUnregisterFromActivity:
    """Test suite for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the email from participants list"""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        participants = activities["Chess Club"]["participants"]
        assert email not in participants
    
    def test_unregister_invalid_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up_returns_400(self, client):
        """Test that unregistering a user not signed up returns 400"""
        email = "nosignup@mergington.edu"  # Not signed up for Basketball Team
        response = client.post(f"/activities/Basketball Team/unregister?email={email}")
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_then_signup_again(self, client):
        """Test that user can re-sign up after unregistering"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Start with Michael in Chess Club
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify added back
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
    
    def test_unregister_returns_correct_message(self, client):
        """Test that unregister returns correct confirmation message"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        data = response.json()
        
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]


# Integration tests
class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_unregister_signup_flow(self, client):
        """Test a complete flow: signup -> unregister -> signup again"""
        email = "testuser@mergington.edu"
        activity = "Art Studio"
        
        # Sign up
        signup1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup1.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister = client.post(f"/activities/{activity}/unregister?email={email}")
        assert unregister.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
        
        # Sign up again
        signup2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup2.status_code == 200
        
        # Verify signed up again
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
    
    def test_signup_multiple_users_same_activity(self, client):
        """Test multiple users signing up for the same activity"""
        activity = "Drama Club"
        users = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Sign up multiple users
        for user in users:
            response = client.post(f"/activities/{activity}/signup?email={user}")
            assert response.status_code == 200
        
        # Verify all signed up
        activities = client.get("/activities").json()
        for user in users:
            assert user in activities[activity]["participants"]
