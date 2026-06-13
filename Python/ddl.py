import clingo
import os
import parser

deontic_dir = "Engine/"
engine_file = [
    os.path.join(deontic_dir, "base.asp"),
    os.path.join(deontic_dir, "language.asp"),
    os.path.join(deontic_dir, "defeasible-ab.asp"),
    os.path.join(deontic_dir, "deontic-comp.asp"),
]

output = """
    #show .
    #show obligation/1.
    #show permitted(X) : permission(X), not obligation(X).
    #show fact/1.
    #show hold(X): defeasible(X), not fact(X).
    #show prohibition(X) : obligation(non(X)).
    #show violation/1.
    #show violatedRule/1.    
    """
    
def execute(theory, format="dft"):
    ctl = clingo.Control(["0", "--warn=no-atom-undefined"])
    ctl.add("base", [], output)

    for f in engine_file:
        ctl.load(f)

    obligations = []
    prohibitions = []
    permissions = []
    facts = []
    defeasibles = []    
    violations = []
    violated = []

    if format == "dft":
        p = parser.DDLParser(sep="&")
        p.parse(theory)
        parsed = p.get_output()
    else:
        parsed = theory

    ctl.add("base", [], parsed)
    ctl.ground([("base", [])])
    for models in ctl.solve(yield_=True):
        for atom in models.symbols(shown=True):
            if atom.name == "obligation" and len(atom.arguments) == 1:
                if atom.arguments[0].name == "non":
                    prohibitions.append(str(f"{atom.arguments[0].arguments[0]}"))
                else:
                    obligations.append(str(atom.arguments[0]))
            elif atom.name == "permitted":
                if atom.arguments[0].name == "non":
                    permissions.append(str(f"~{atom.arguments[0].arguments[0]}"))
                else:
                    permissions.append(str(atom.arguments[0]))
            elif atom.name == "fact":
                if atom.arguments[0].name == "non":
                    facts.append(str(f"~{atom.arguments[0].arguments[0]}"))
                else:
                    facts.append(str(atom.arguments[0]))
            elif atom.name == "hold":
                if atom.arguments[0].name == "non":
                    defeasibles.append(str(f"~{atom.arguments[0].arguments[0]}"))
                else:
                    defeasibles.append(str(atom.arguments[0]))   
            elif atom.name == "violation":
                if atom.arguments[0].name == "non":
                    violations.append(str(f"~{atom.arguments[0].arguments[0]}"))
                else:
                    violations.append(str(atom.arguments[0]))
            elif atom.name == "violatedRule":             
                 violated.append(str(atom.arguments[0]))

        # for atom in models.symbols(atoms=True):
        #     # if atom.name == "rule":
        #     #     print(atom)
        #     # if atom.name == "superior":
        #     #     print(atom)
        #     # if atom.name == "atom":
        #     #     print (atom.arguments[0])
        #     # if atom.name == "permission":
        #     #     print(atom)
        #     # if atom.name == "opposes":
        #     #     print(atom)
        #     if atom.name == "body":
        #         print(atom)
                
 
    if facts:
        print(f"Facts:")
        for f in facts:
            print(f"  {f}")

    if defeasibles:    
        print("\nHold:")
        for d in defeasibles:
            print(f"  {d}")

    if obligations:    
        print("\nObligations:")
        for o in obligations:
            print(f"  {o}")
    
    if prohibitions:
        print("\nProhibitions:")
        for p in prohibitions:
            print(f"  {p}")
        
    if permissions:
        print("\nPermissions:")
        for p in permissions:
            print(f"  {p}")

    if violations:
        print("\nViolations:")
        for v in violations:
            print(f"  {v}")

    if violated:
        print("\nViolated rules:")
        for r in violated:
            print(f"  {r}")

    times = ctl.statistics['summary']['times']
    print(f"\nTotal: {times['total']:.3f}s")
    print(f"CPU:   {times['cpu']:.3f}s")
