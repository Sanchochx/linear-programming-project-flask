from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
import pulp


app= Flask(__name__)
Bootstrap5(app)

@app.route("/")
def home():
    return render_template("inicio.html")

@app.route("/calculadora")
def calculadora():
    return render_template("index.html")

@app.route("/solve", methods=['POST'])
def solve():
    maximize = True if request.form.get('optimization_type') == 'maximizar' else False
    objective_coefficients = [float(request.form.get(f'coef_{i}')) for i in range(1, 4)]
    constraint_entries_list = [[float(request.form.get(f'constraint_{i}_{j}')) for j in range(3)] for i in range(3)]
    relation_operators = [request.form.get(f'relation_{i}') for i in range(3)]
    constraint_constants = [float(request.form.get(f'constant_{i}')) for i in range(3)]

    # Definir problema
    problem = pulp.LpProblem("Problema Programación Lineal", pulp.LpMaximize if maximize else pulp.LpMinimize)

    # Definir variables
    decision_vars = [pulp.LpVariable(f'x{i}', lowBound=0) for i in range(1, 4)]

    # Construir funcion objetivo
    objective = pulp.lpSum([coef * var for coef, var in zip(objective_coefficients, decision_vars)])
    problem += objective

    # Constantes
    for i, constraint_coeffs in enumerate(constraint_entries_list):
        if relation_operators[i] == '<=':
            problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) <= constraint_constants[i]
        elif relation_operators[i] == '>=':
            problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) >= constraint_constants[i]
        elif relation_operators[i] == '=':
            problem += pulp.lpSum([coef * var for coef, var in zip(constraint_coeffs, decision_vars)]) == constraint_constants[i]

    # Resolver
    problem.solve()

    # Solucion
    solution = {'vars': [], 'optimal_value': pulp.value(problem.objective)}
    for var in problem.variables():
        solution['vars'].append({var.name: var.varValue})

    return render_template('solution.html', solution=solution)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
