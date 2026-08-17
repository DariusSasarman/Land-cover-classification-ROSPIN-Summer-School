## Branches

| Branch | Description        |
|--------|---------------------|
| main   | Cod stabil, functional |
| rares  | Branch-ul lui Rares |
| maria  | Branch-ul Mariei    |
| oliver | Branch-ul lui Oliver |
| darius | Branch-ul lui Darius |
| antonio | Branch-ul lui Antonio |

## Prima configurare

```bash
git clone <url-repo>
cd land-cover-classification
```
 
**Daca branch-ul tau nu exista inca**, îl creezi:
```bash
git checkout -b darius        # creează branch-ul local și te muți pe el
git push -u origin darius     # îl trimite pe GitHub, prima dată
```
 
**Dacă branch-ul există deja** (l-ai creat anterior):
```bash
git checkout darius
```

## Flux zilnic

**1. Inainte sa lucrezi - actualizezi branch-ul tau:**
```bash
git checkout main
git pull origin main
git checkout darius
git merge main
```

**2. Lucrezi, salvezi progresul:**
```bash
git add .
git commit -m "add cloud masking function"
git push origin darius
```

**3. Cand codul merge - il integrezi in main:**
```bash
git checkout main
git pull origin main
git merge darius
git push origin main
```

## Rezumat vizual

```
main    ──────────●──────────────●──────
                 ↑                ↑
darius  ──●───●──┘      ●────●────┘
oliver       ────●───●─────────────●────
```

## Reguli

- Nu lucra direct pe `main`.
- Pull inainte de merge, ca sa eviti conflicte.
- Testeaza codul inainte sa-l pui pe main.
- Mesaje de commit clare, nu "wip".

## Conflict

```
<<<<<<< darius
codul tau
=======
codul din main
>>>>>>> main
```
Alegi ce pastrezi, stergi liniile `<<<<`/`====`/`>>>>`, apoi:
```bash
git add .
git commit -m "resolve merge conflict"
```

## Comenzi utile

| Comanda | Ce face |
|---|---|
| `git status` | fisiere modificate |
| `git log --oneline` | istoric commit-uri |
| `git diff` | ce s-a schimbat |
| `git fetch origin` | verifici noutati pe GitHub, fara sa le aduci |