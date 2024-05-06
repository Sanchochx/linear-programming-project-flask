from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
import pulp


app= Flask(__name__)
Bootstrap5(app)

@app.route("/")
def home():
    return render_template("inicio.html")

@app.route("/index", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_constraints = int(request.form['num_constraints'])
        num_variables = int(request.form['num_variables'])
        optimization_type = request.form['optimization_type']
        return redirect(url_for('calculator', num_constraints=num_constraints, num_variables=num_variables,
                                optimization_type=optimization_type))
    return render_template('index.html')

@app.route("/calculator", methods=['GET', 'POST'])
def calculator():
    if request.method == 'POST':
        num_variables = int(request.form['num_variables'])
        num_constraints = int(request.form['num_constraints'])
        optimization_type = request.form['optimization_type']

        objective_coefficients = [float(request.form.get(f'coef_{i}')) for i in range(1, num_variables + 1)]
        constraint_entries_list = [[float(request.form.get(f'constraint_{i}_{j}')) for j in range(1, num_variables + 1)]
                                   for i in range(1, num_constraints + 1)]
        relation_operators = [request.form.get(f'relation_{i}') for i in range(1, num_constraints + 1)]
        constraint_constants = [float(request.form.get(f'constant_{i}')) for i in range(1, num_constraints + 1)]

        problem = pulp.LpProblem("Problema de Programación Lineal",
                                 pulp.LpMaximize if optimization_type == 'Maximizar' else pulp.LpMinimize)

        decision_vars = [pulp.LpVariable(f'x{i}', lowBound=0) for i in range(1, num_variables + 1)]

        objective = pulp.lpSum([coef * var for coef, var in zip(objective_coefficients, decision_vars)])
        problem += objective

        for i, constraint_coeffs in enumerate(constraint_entries_list):
            if relation_operators[i] == '<=':
                problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) <= \
                           constraint_constants[i]
            elif relation_operators[i] == '>=':
                problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) >= \
                           constraint_constants[i]
            elif relation_operators[i] == '=':
                problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) == \
                           constraint_constants[i]

        problem.solve()

        solution = {'vars': [], 'optimal_value': pulp.value(problem.objective)}
        for var in problem.variables():
            solution['vars'].append({var.name: var.varValue})

        return render_template('solution.html', solution=solution)

    num_constraints = request.args.get('num_constraints', type=int)
    num_variables = request.args.get('num_variables', type=int)
    optimization_type = request.args.get('optimization_type')
    return render_template('calculator.html', num_constraints=num_constraints, num_variables=num_variables,
                           optimization_type=optimization_type)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
