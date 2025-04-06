import time
from app import create_app, db
from flask import render_template_string
from app.auth.routes import createTestUser
from app.listeners.routes import testEditLanguage
from sqlalchemy.exc import OperationalError


# ======== TESTING ROUTES ========
# These routes are for testing purposes only and should be removed once the frontend is in place
# These routes are used to simulate the frontend form submissions
# The frontend will make POST requests to these routes with the form data
# The form data will be validated and then used to create a new user in the database

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Index Page</title>
    </head>
    <body>
        <h1>Welcome to the User Management System</h1>
        <p>Use the links below to register a Listener or a Researcher:</p>
        <ul>
            <li><a href="/userResetPassword">Reset User Password #w orking</a></li>
            <li><a href="/blindEmailParse">Blind Email Parse # working</a></li>
            <li><a href="/blindPasswordReset">Blind Password Reset # working</a></li>
            <li><a href="/createProject">Create Project # working</a></li>
            <li><a href="/updateProjectName">Update Project Name # working</a></li>
            <li><a href="/addProjectTags">Add Project Tags # working</a></li>
            <li><a href="/removeProjectTags">Remove Project Tags # working</a></li>
            <li><a href="/searchProjectByTag">Search Project By Tag # working</a></li>
            <li><a href="/updateProjectStatus">Update Project Status # working</a></li>
            <li><a href="/getProjects">Get Projects # working</a></li>
            <li><a href="/getProject">Get Project # working</a></li>
            <li><a href="/deleteProject">Delete Project # working</a></li>
            <li><a href="/setProjectMetricField">Set Project Metrics Field # working</a></li>
            <li><a href="/getProjectMetrics">Get Project Metrics # working</a></li>
            <li><a href="/updateProjectMetrics">Update Project Metrics # working</a></li>
            <li><a href="/deleteProjectMetrics">Delete Project Metrics # working</a></li>
            <li><a href="/testUploadAudio">Test Audio uploading function # idkidk </a></li>
            <li><a href="/testAddLang">Test add language function </a></li>
            <li><a href="/getListenerData">Test get user data function </a></li>
        </ul>
    </body>
    </html>
    ''')

@app.route('/userResetPassword', methods=['GET'])
def userResetPasswordForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
    </head>
    <body>
        <h1>User Reset Password</h1>
        <form action="/userResetPassword" method="post">
            <label for="pw">New Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="pw_confirmation">Confirm Password:</label><br>
            <input type="password" id="pw_confirmation" name="pw_confirmation"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/userResetPassword', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/blindEmailParse', methods=['GET'])
def blindEmailParseForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Email Parse</title>
    </head>
    <body>
        <h1>Blind Email Parse</h1>
        <form action="/blindEmailParse" method="post">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/blindEmailParse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/blindPasswordReset', methods=['GET'])
def blindPasswordResetForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Password Reset</title>
    </head>
    <body>
        <h1>Blind Password Reset</h1>
        <form action="/blindPasswordReset" method="post">
            <label for="id">Blind ID:</label><br>
            <input type="text" id="id" name="id"><br>
            <label for="pw">New Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="pw_confirmation">Confirm Password:</label><br>
            <input type="password" id="pw_confirmation" name="pw_confirmation"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/blindPasswordReset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/updateProjectName', methods=['GET'])
def updateProjectForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Name</title>
    </head>
    <body>
        <h1>Update Project Name</h1>
        <form action="/updateProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="new_project_name">New Project Name:</label><br>
            <input type="text" id="new_project_name" name="new_project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectName', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/addProjectTags', methods=['GET'])
def addProjectTagsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Project Tags</title>
    </head>
    <body>
        <h1>Add Project Tags</h1>
        <form action="/addProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/addProjectTags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/removeProjectTags', methods=['GET'])
def removeProjectTagsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Remove Project Tags</title>
    </head>
    <body>
        <h1>Remove Project Tags</h1>
        <form action="/removeProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/removeProjectTags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/updateProjectStatus', methods=['GET'])
def updateProjectStatusForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Status</title>
    </head>
    <body>
        <h1>Update Project Status</h1>
        <form action="/updateProjectStatus" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="status">Status:</label><br>
            <input type="text" id="status" name="status"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectStatus', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProjects', methods=['GET'])
def getProjectsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Projects</title>
    </head>
    <body>
        <h1>Get Projects</h1>
        <button id="getProjects">Get Projects</button>
        <script>
            document.getElementById('getProjects').addEventListener('click', function () {
                fetch('/getProjects', {
                    method: 'GET'
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProject', methods=['GET'])
def getProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project</title>
    </head>
    <body>
        <h1>Get Project</h1>
        <form action="/getProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/deleteProject', methods=['GET'])
def deleteProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project</title>
    </head>
    <body>
        <h1>Delete Project</h1>
        <form action="/deleteProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/setProjectMetricField', methods=['GET'])
def setProjectMetricFieldForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Set Project Metrics</title>
        <style>
            .metric-input { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Set Project Metrics</h1>
        <form id="metricsForm" action="/setProjectMetricField" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>

            <div id="metricsContainer">
                <div class="metric-input">
                    <label for="metric_1">Metric Name:</label>
                    <input type="text" id="metric_1" name="metric_name_1" placeholder="Metric Name" required>
                    <label for="value_1">Value:</label>
                    <input type="number" id="value_1" name="metric_value_1" placeholder="Value" required>
                </div>
            </div>

            <button type="button" id="addMetric">Add Metric</button><br><br>
            <button type="submit">Submit</button>
        </form>

        <script>
            let metricCount = 1;

            // Add a new metric input field
            document.getElementById('addMetric').addEventListener('click', function () {
                metricCount++;
                const metricsContainer = document.getElementById('metricsContainer');
                const newMetricDiv = document.createElement('div');
                newMetricDiv.className = 'metric-input';
                newMetricDiv.innerHTML = `
                    <label for="metric_${metricCount}">Metric Name:</label>
                    <input type="text" id="metric_${metricCount}" name="metric_name_${metricCount}" placeholder="Metric Name" required>
                    <label for="value_${metricCount}">Value:</label>
                    <input type="number" id="value_${metricCount}" name="metric_value_${metricCount}" placeholder="Value" required>
                `;
                metricsContainer.appendChild(newMetricDiv);
            });

            // Handle form submission
            document.getElementById('metricsForm').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);

                // Convert form data into JSON format
                const jsonData = {};
                const metrics = {};
                for (const [key, value] of formData.entries()) {
                    if (key.startsWith('metric_name_')) {
                        const metricIndex = key.split('_')[2]; // Extract the index from the key
                        metrics[formData.get(`metric_name_${metricIndex}`)] = parseFloat(formData.get(`metric_value_${metricIndex}`)) || 0;
                    } else if (key !== `metric_value_${key.split('_')[2]}`) {
                        jsonData[key] = value; // Add other fields like project_name
                    }
                }
                jsonData.metrics = metrics;

                // Send the data to the backend
                fetch('/setProjectMetricField', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProjectMetrics', methods=['GET'])
def getProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project Metrics</title>
    </head>
    <body>
        <h1>Get Project Metrics</h1>
        <form action="/getProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/updateProjectMetrics', methods=['GET'])
def updateProjectMetricsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Metrics</title>
    </head>
    <body>
        <h1>Update Project Metrics</h1>
        <form action="/updateProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>
            <label for="metrics">Metrics (Data input format: key1:value1, key2:value2):</label><br>
            <input type="text" id="metrics" name="metrics" placeholder="key1:value1, key2:value2" required><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert metrics to a dictionary
                const metrics = {};
                const metricsArray = jsonData.metrics.split(',');
                for (const metric of metricsArray) {
                    const [key, value] = metric.split(':');
                    metrics[key] = parseFloat(value) || 0;
                }
                // ensure metrics is a dictionary
                if (typeof metrics !== 'object') {
                    console.error('Metrics must be a dictionary');
                    return;
                }

                jsonData.metrics = metrics;

                // Send the parsed data to the backend
                fetch('/updateProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/deleteProjectMetrics', methods=['GET'])
def deleteProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project Metrics</title>
    </head>
    <body>
        <h1>Delete Project Metrics</h1>
        <form action="/deleteProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="metric">Metric:</label><br>
            <input type="text" id="metric" name="metric"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/searchProjectByTag', methods=['GET'])
def searchProjectByTagForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Project By Tag</title>
    </head>
    <body>
        <h1>Search Project By Tag</h1>
        <form action="/searchProjectByTag" method="post">
            <label for="tag">Tag:</label><br>
            <input type="text" id="tag" name="tag"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/searchProjectByTag', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/testUploadAudio', methods=['GET'])
def audioFileUploadForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audio file upload testing</title>
    </head>
    <body>
        <h1>Audio file upload</h1>
        <form id="uploadForm">
            <label for="audio">Upload Audio File:</label><br>
            <input type="file" id="audio" name="audio" accept="audio/*"><br><br>

            <button type="submit">Submit</button>
        </form>

        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();

                const formData = new FormData(e.target);

                fetch('/uploadAudioFile', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                .then(data => console.log(data));
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/testAddLang', methods=['GET'])
def testAddLanguageForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add language</title>
    </head>
    <body>
        <h1>User Add Language</h1>
        <form action="/addLanguage" method="post">
            <label for="language">Language:</label><br>
            <input type="text" id="language" name="language"><br>
            <label for="proficiency">Proficiency level:</label><br>
            <input type="text" id="proficiency" name="proficiency"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/addLanguage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getListenerData', methods=['GET'])
def getListenerDataForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Listener</title>
    </head>
    <body>
        <h1>Get Listener</h1>
        <form action="/getListeners" method="post">
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                fetch('/getListeners', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify("")
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

# ======== END OF TESTING ROUTES ========


# ========== Run the Flask App ==========

app = create_app()

if __name__ == '__main__':
    for _ in range(5):
        try:
            with app.app_context():
            # initialize the database
                db.create_all()
                createTestUser()
                testEditLanguage()
                # creates test user for frontend testing, verification for this account is waived
                # testAddLanguage() # for testing add language functionality; To be removed
            break
        except OperationalError as e:
            print("Database not ready yet, retrying...")
            time.sleep(5)
    else:
        print("Database failed to initialize, exiting...")
        exit(1)
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)
