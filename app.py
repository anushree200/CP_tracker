from flask import Flask, render_template, request, jsonify
import sqlite3,os,json,subprocess,tempfile

app = Flask(__name__)

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
        {"id": p[0], "title": p[1], "description": p[2], "points": p[3], "topic": p[4]}
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
    # Get the problem details
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    problem = cur.fetchone()
    conn.close()

    if problem is None:
        return jsonify({"error": "Problem not found"}), 404

    # Get the submitted code and language
    code = request.form.get('code')
    language = request.form.get('language')

    if not code or not language:
        return jsonify({"error": "Code or language not provided"}), 400

    # For simplicity, only handle Python in this example
    if language != 'Python':
        return jsonify({"error": "Only Python is supported in this example"}), 400

    # Parse test cases
    test_inputs = json.loads(problem[5])  # test_inputs
    test_outputs = json.loads(problem[6])  # test_outputs

    # Run the code for each test case
    results = []
    for test_input, expected_output in zip(test_inputs, test_outputs):
        try:
            # Write the code to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file_name = f.name

            # Run the code with the test input
            process = subprocess.run(
                ['python', temp_file_name],
                input=test_input,
                text=True,
                capture_output=True,
                timeout=5  # 5-second timeout to prevent infinite loops
            )

            # Clean up the temporary file
            os.remove(temp_file_name)

            # Get the output and errors
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
            else:
                # Compare the actual output with the expected output
                if actual_output == expected_output:
                    verdict = "Accepted"
                else:
                    verdict = "Wrong Answer"
                
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
        test_inputs = request.form.get('test_inputs')
        test_outputs = request.form.get('test_outputs')

        # Validate inputs
        if not all([title, description, points, topic, test_inputs, test_outputs]):
            return jsonify({"success": False, "error": "All fields are required"}), 400

        # Parse test cases
        test_inputs = json.loads(test_inputs)
        test_outputs = json.loads(test_outputs)

        if len(test_inputs) < 3 or len(test_outputs) < 3:
            return jsonify({"success": False, "error": "At least 3 test cases are required"}), 400

        # Get the next problem ID
        conn = sqlite3.connect("problems.db")
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM problems")
        max_id = cur.fetchone()[0]
        new_id = (max_id if max_id is not None else 0) + 1

        # Insert the new problem into the database
        cur.execute("""
            INSERT INTO problems (id, title, description, points, topic, test_inputs, test_outputs)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (new_id, title, description, int(points), topic, json.dumps(test_inputs), json.dumps(test_outputs)))

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)