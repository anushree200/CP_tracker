from flask import Flask, render_template, request, jsonify,session,flash,redirect,url_for
import sqlite3,os,json,subprocess,tempfile,datetime

app = Flask(__name__)
app.secret_key = 'tl_cp_tracker'
f = open("C:\\Users\\aanuu\\Downloads\\TL_DEV_MINI\\CP_tracker\\log.txt", 'a')
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin' in session:
        redirect_url = request.args.get('redirect', url_for('frontpage'))
        return redirect(redirect_url)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('admin.db')
        cur = conn.cursor()
        cur.execute('SELECT pwd FROM admin WHERE username = ?', (username,))
        result = cur.fetchone()
        conn.close()

        if result and result[0] == password:
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
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems")
    problems = cur.fetchall()
    conn.close()
    return render_template("problemspage.html", problems=problems)

@app.route('/filter')
def filter_problems():
    points = request.args.get('points', '')
    topic = request.args.get('topic', '')
    keywords = request.args.get('keywords', '')

    query = "SELECT * FROM problems WHERE 1=1"
    params = []

    if points:
        query += " AND points = ?"
        params.append(int(points))
    
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    
    if keywords:
        query += " AND title LIKE ?"
        params.append(f"%{keywords}%")

    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute(query, params)
    problems = cur.fetchall()
    conn.close()

    problems_list = [
    {
        "id": p[0], "title": p[1], "description": p[2],
        "points": p[3], "topic": p[4],
        "attempts": p[7], "solved": p[8]
    }
    for p in problems
]

    return jsonify(problems_list)

@app.route('/problem/<int:problem_id>')
def problem_detail(problem_id):
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    problem = cur.fetchone()
    conn.close()

    if problem is None:
        return "Problem not found", 404
    test_inputs = json.loads(problem[5])
    test_outputs = json.loads(problem[6])
    return render_template("problemdetail.html", problem=problem, test_inputs=test_inputs,test_outputs=test_outputs)

@app.route('/submit/<int:problem_id>', methods=['POST'])
def submit_code(problem_id):
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    problem = cur.fetchone()

    if problem is None:
        conn.close()
        return jsonify({"error": "Problem not found"}), 404

    code = request.form.get('code')
    language = request.form.get('language')

    if not code or not language:
        conn.close()
        return jsonify({"error": "Code or language not provided"}), 400

    if language != 'Python':
        return jsonify({"error": "Only Python is supported in this example"}), 400

    test_inputs = json.loads(problem[5])
    test_outputs = json.loads(problem[6])
    results = []
    all_correct = True
    verdict = "Accepted" 

    for test_input, expected_output in zip(test_inputs, test_outputs):
        try:
            processed_input = test_input.replace(',', ' ')
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_f:
                temp_f.write(code)
                temp_file_name = temp_f.name

            process = subprocess.run(
                ['python', temp_file_name],
                input=processed_input,
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

    cur.execute("UPDATE problems SET attempts = attempts + 1, solved = ? WHERE id = ?",
                (1 if all_correct else 0, problem_id))
    conn.commit()
    conn.close()

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include date and time
    problem_id = problem[0]
    problem_title = problem[1]
    status = "Success" if all_correct else f"Failure ({verdict})"
    log_entry = f"Problem ID: {problem_id}, Title: {problem_title}, Date and Time: {timestamp}, Status: {status}\n"
    f.write(log_entry)
    f.flush()

    return jsonify({"results": results})
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

        conn = sqlite3.connect("problems.db")
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM problems")
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id is not None else 0) + 1

        cur.execute("""
            INSERT INTO problems (id, title, description, points, topic, test_inputs, test_outputs,attempts,solved,platformname,link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_id, title, description, int(points), topic, json.dumps(test_inputs), json.dumps(test_outputs),0,0, platform, platform_link))

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/problem/<int:problem_id>/edit', methods=['GET', 'POST'])
def edit_problem(problem_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login', redirect=request.url))

    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    problem = cur.fetchone()
    conn.close()

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
            conn = sqlite3.connect("problems.db")
            cur = conn.cursor()
            cur.execute("""
                UPDATE problems 
                SET title = ?, description = ?, points = ?, topic = ?, test_inputs = ?, test_outputs = ?
                WHERE id = ?
            """, (title, description, int(points), topic, json.dumps(test_inputs), json.dumps(test_outputs), problem_id))
            conn.commit()
            conn.close()

            flash("Problem updated successfully!", "success")
            return redirect(url_for('frontpage'))

        except Exception as e:
            flash(f"Error updating problem: {str(e)}", "error")
            return render_template('edit_problem.html', problem=problem)

    return render_template('edit_problem.html', problem=problem)

@app.route('/stats')
def stats():
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()

    # Total submissions (sum of attempts across all problems)
    cur.execute("SELECT SUM(attempts) FROM problems")
    total_submissions = cur.fetchone()[0] or 0

    # Number of successful submissions (count of problems where solved = 1)
    cur.execute("SELECT COUNT(*) FROM problems WHERE solved = 1")
    successful_submissions = cur.fetchone()[0]

    # Success percentage (accuracy)
    success_percentage = (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0
    success_percentage = round(success_percentage, 2)

    failure_percentage = 100 - success_percentage if total_submissions > 0 else 0
    failure_percentage = round(failure_percentage, 2)

    conn.close()

    # Read the submission log
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
    "submission_log": submission_log
    }

    return render_template("stats.html", stats=stats_data)


if __name__ == '__main__':
    app.run(debug=True)