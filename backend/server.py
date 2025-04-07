import time
from app import create_app, db
from app.auth.routes import createTestUser
from app.projects.routes import testUploadAudioFile
from app.listeners.routes import testChangeDemographics, testGetListener
from sqlalchemy.exc import OperationalError


# ========== Flask App Initialization ==========

app = create_app()

# ========== Run the Flask App ==========

if __name__ == '__main__':
    for _ in range(5):
        try:
            with app.app_context():
            # initialize the database
                db.create_all()
                createTestUser()
                # testEditLanguage()
                # creates test user for frontend testing, verification for this account is waived
                # testAddLanguage() # for testing add language functionality; To be removed
                testUploadAudioFile()
                testChangeDemographics()
            break
        except OperationalError as e:
            print("Database not ready yet, retrying...")
            time.sleep(5)
    else:
        print("Database failed to initialize, exiting...")
        exit(1)
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)
