from src.app import activities


def test_root_redirects_to_static_site(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"] == activities["Chess Club"]


def test_signup_adds_student_to_activity(client):
    email = "alex@mergington.edu"

    response = client.post("/activities/Soccer Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Club"}
    assert email in activities["Soccer Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_student(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_full_activity(client):
    activity = activities["Soccer Club"]
    activity["participants"] = [
        f"student{index}@mergington.edu" for index in range(activity["max_participants"])
    ]

    response = client.post(
        "/activities/Soccer Club/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert "alex@mergington.edu" not in activity["participants"]


def test_unregister_removes_student_from_activity(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_absent_student(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "alex@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_unregister_rejects_unknown_activity(client):
    response = client.delete("/activities/Unknown/signup", params={"email": "alex@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}