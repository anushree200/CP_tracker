from flask import Flask, render_template, request, jsonify,session,flash,redirect,url_for
import os,json,subprocess,tempfile,datetime
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'tl_cp_tracker'
f = open("C:\\Users\\aanuu\\Downloads\\TL_DEV_MINI\\CP_tracker\\log.txt", 'a')

client = MongoClient("mongodb+srv://axxshxxe20:aoWa1PDYvM78QgtX@cluster0.czqryun.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['cp_tracker']
admin_collection = db['admins']
problems = db['problems']
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        redirect_url = request.args.get('redirect', url_for('frontpage'))
        return redirect(redirect_url)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = admin_collection.find_one({"username": username})

        if admin and admin["pwd"] == password:
            session['admin'] = username
            redirect_url = request.args.get('redirect', url_for('frontpage')) 
            flash('Login successful!', 'success')
            return redirect(redirect_url)
        else:
            flash('Invalid username or password', 'error')
            return render_template('admin_login.html', redirect=request.args.get('redirect', ''))

    return render_template('admin_login.html', redirect=request.args.get('redirect', ''))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('frontpage'))


@app.route('/')
def frontpage():
    problem_docs = list(problems.find())
    return render_template("problemspage.html", problems=problem_docs)


@app.route('/filter')
def filter_problems():
    points = request.args.get('points', '')
    topic = request.args.get('topic', '')
    keywords = request.args.get('keywords', '')

    query = {}

    if points:
        query['points'] = int(points)
    if topic:
        query['topic'] = topic
    if keywords:
        query['title'] = {'$regex': keywords, '$options': 'i'}  # Case-insensitive match

    filtered = problems.find(query)

    problems_list = [
        {
            "id": str(p["_id"]),
            "title": p["title"],
            "description": p.get("description", ""),
            "points": p.get("points", 0),
            "topic": p.get("topic", ""),
            "attempts": p.get("attempts", 0),
            "solved": p.get("solved", 0)
        }
        for p in filtered
    ]

    return jsonify(problems_list)

from bson.objectid import ObjectId

@app.route('/problem/<problem_id>')
def problem_detail(problem_id):
    try:
        problem = problems.find_one({"_id": ObjectId(problem_id)})
    except:
        return "Invalid problem ID", 400

    if problem is None:
        return "Problem not found", 404

    test_inputs = json.loads(problem.get('test_inputs', '[]'))
    test_outputs = json.loads(problem.get('test_outputs', '[]'))

    return render_template("problemdetail.html", problem=problem, test_inputs=test_inputs, test_outputs=test_outputs)

@app.route('/submit/<problem_id>', methods=['POST'])
def submit_code(problem_id):
    try:
        problem = problems.find_one({"_id": ObjectId(problem_id)})
    except:
        return jsonify({"error": "Invalid problem ID format"}), 400

    if problem is None:
        return jsonify({"error": "Problem not found"}), 404

    code = request.form.get('code')
    language = request.form.get('language')

    if not code or not language:
        return jsonify({"error": "Code or language not provided"}), 400

    if language != 'Python':
        return jsonify({"error": "Only Python is supported in this example"}), 400

    test_inputs = json.loads(problem['test_inputs'])
    test_outputs = json.loads(problem['test_outputs'])
    results = []
    all_correct = True
    verdict = "Accepted"

    for test_input, expected_output in zip(test_inputs, test_outputs):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_f:
                temp_f.write(code)
                temp_file_name = temp_f.name

            process = subprocess.run(
                ['python', temp_file_name],
                input=test_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            os.remove(temp_file_name)

            actual_output = process.stdout.strip()
            error = process.stderr.strip()

            if error:
                results.append({
                    "input": test_input,
                    "expected_output": expected_output,
                    "actual_output": actual_output,
                    "error": error,
                    "verdict": "Runtime Error"
                })
                all_correct = False
                verdict = "Runtime Error"
            else:
                if actual_output == expected_output:
                    verdict = "Accepted"
                else:
                    verdict = "Wrong Answer"
                    all_correct = False

                results.append({
                    "input": test_input,
                    "expected_output": expected_output,
                    "actual_output": actual_output,
                    "error": "",
                    "verdict": verdict
                })

        except subprocess.TimeoutExpired:
            os.remove(temp_file_name)
            results.append({
                "input": test_input,
                "expected_output": expected_output,
                "actual_output": "",
                "error": "Time Limit Exceeded",
                "verdict": "Time Limit Exceeded"
            })
            all_correct = False
            verdict = "Time Limit Exceeded"
        except Exception as e:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            results.append({
                "input": test_input,
                "expected_output": expected_output,
                "actual_output": "",
                "error": str(e),
                "verdict": "Error"
            })
            all_correct = False
            verdict = f"Error: {str(e)}"

    # Update attempts and solved in MongoDB
    update_fields = {"$inc": {"attempts": 1}}
    if all_correct:
        update_fields["$set"] = {"solved": 1}
    problems.update_one({"_id": ObjectId(problem_id)}, update_fields)

    # Logging
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    problem_title = problem['title']
    status = "Success" if all_correct else f"Failure ({verdict})"
    log_entry = f"Problem ID: {problem_id}, Title: {problem_title}, Date and Time: {timestamp}, Status: {status}\n"
    f.write(log_entry)
    f.flush()

    return jsonify({"results": results})

@app.route('/save_note/<int:problem_id>', methods=['POST'])
def save_note(problem_id):
    note = request.form.get('note', '')
    result = db.problems.update_one(
        {"id": int(problem_id)},
        {"$set": {"note": note}}
    )
    
    if result.matched_count == 0:
        return jsonify({"success": False, "error": "Problem not found"}), 404

    return jsonify({"success": True})

@app.route('/newproblem')
def newproblem():
    return render_template("newproblem.html")

@app.route('/addproblem', methods=['POST'])
def add_problem():
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        points = request.form.get('points')
        topic = request.form.get('topic')
        platform = request.form.get('platform')
        platform_link = request.form.get('platform_link')
        test_inputs = request.form.get('test_inputs')
        test_outputs = request.form.get('test_outputs')

        if not all([title, description, points, topic, test_inputs, test_outputs]):
            return jsonify({"success": False, "error": "All fields are required"}), 400

        test_inputs = json.loads(test_inputs)
        test_outputs = json.loads(test_outputs)

        if len(test_inputs) < 3 or len(test_outputs) < 3:
            return jsonify({"success": False, "error": "At least 3 test cases are required"}), 400

        max_problem = problems.find_one(sort=[("id", -1)])
        new_id = (max_problem['id'] if max_problem else 0) + 1

        problem_doc = {
            "id": new_id,
            "title": title,
            "description": description,
            "points": int(points),
            "topic": topic,
            "test_inputs": test_inputs,
            "test_outputs": test_outputs,
            "attempts": 0,
            "solved": 0,
            "platformname": platform,
            "link": platform_link,
            "note": "add your notes here"
        }

        problems.insert_one(problem_doc)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/problem/<problem_id>/edit', methods=['GET', 'POST'])
def edit_problem(problem_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login', redirect=request.url))

    problem = problems.find_one({"id": int(problem_id)})

    if problem is None:
        flash("Problem not found.", "error")
        return redirect(url_for('frontpage'))

    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            points = request.form.get('points')
            topic = request.form.get('topic')
            test_inputs = request.form.get('test_inputs')
            test_outputs = request.form.get('test_outputs')

            if not all([title, description, points, topic, test_inputs, test_outputs]):
                flash("All fields are required.", "error")
                return render_template('edit_problem.html', problem=problem)

            try:
                test_inputs = json.loads(test_inputs) if test_inputs else []
                test_outputs = json.loads(test_outputs) if test_outputs else []
            except json.JSONDecodeError:
                flash("Test inputs and outputs must be valid JSON.", "error")
                return render_template('edit_problem.html', problem=problem)

            if len(test_inputs) < 3 or len(test_outputs) < 3:
                flash("At least 3 test cases are required.", "error")
                return render_template('edit_problem.html', problem=problem)
            update_result = problems.update_one(
                {"id": int(problem_id)},
                {"$set": {
                    "title": title,
                    "description": description,
                    "points": int(points),
                    "topic": topic,
                    "test_inputs": test_inputs,
                    "test_outputs": test_outputs
                }}
            )

            flash("Problem updated successfully!", "success")
            return redirect(url_for('frontpage'))

        except Exception as e:
            flash(f"Error updating problem: {str(e)}", "error")
            return render_template('edit_problem.html', problem=problem)

    return render_template('edit_problem.html', problem=problem)

@app.route('/stats')
def stats():
    pipeline = [
        {"$group": {"_id": None, "total_attempts": {"$sum": "$attempts"}}}
    ]
    result = list(problems.aggregate(pipeline))
    total_submissions = result[0]["total_attempts"] if result else 0
    successful_submissions = problems.count_documents({"solved": 1})

    success_percentage = (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0
    success_percentage = round(success_percentage, 2)

    failure_percentage = 100 - success_percentage if total_submissions > 0 else 0
    failure_percentage = round(failure_percentage, 2)

    pipeline = [
        {"$match": {"solved": 1}},
        {"$group": {"_id": "$points", "count": {"$sum": 1}}}
    ]
    rows = list(problems.aggregate(pipeline))
    point_distribution = {str(row["_id"]): row["count"] for row in rows}
    point_distribution = json.dumps(point_distribution)

    submission_log = []
    log_file_path = "C:\\Users\\aanuu\\Downloads\\TL_DEV_MINI\\CP_tracker\\log.txt"
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            submission_log = log_file.readlines()

    stats_data = {
    "total_submissions": int(total_submissions),
    "successful_submissions": int(successful_submissions),
    "success_percentage": float(success_percentage),
    "failure_percentage": float(failure_percentage),
    "submission_log": submission_log,
    "point_distribution":point_distribution
    }

    return render_template("stats.html", stats=stats_data)


if __name__ == '__main__':
    app.run(debug=True)