---
name: git-pr-review
description: Führt einen gründlichen, ehrlichen und kritischen Code-Review eines Pull Requests durch – GitHub oder Azure DevOps. Nutze diesen Skill immer wenn der User einen PR reviewen, prüfen, analysieren oder begutachten möchte – egal ob mit PR-Link, PR-Nummer oder Beschreibung wie "schau dir PR #42 an", "review meinen PR", "was hältst du von diesem PR" oder "kannst du den PR checken". Auch bei Fragen wie "ist der PR merge-ready?" oder "gibt es Probleme mit dem PR?" direkt anwenden.
compatibility: "GitHub: `gh` CLI (bzw. GitHub MCP). Azure DevOps: `az repos` + git-diff. Plattform wird aus PR-Link/Remote erkannt."
---

# PR Review Skill

Ehrlicher, kritischer, konstruktiver Review: echte Probleme klar benennen, priorisieren, konkrete
Fixes vorschlagen. Kein Loben zum Auffüllen.

**Wann:** Für eigene PRs ist das die Review für **Tier L** (siehe "Risk tiers" im globalen CLAUDE.md).
Bei S/M hat `handover` die Auto-Review schon gemacht — steht im PR-Body ein Abschnitt
`## Auto-review`, und ist der PR S/M, kurz darauf hinweisen und nur auf ausdrücklichen Wunsch
trotzdem reviewen. Fremde PRs: immer.

## 1. Daten laden

**Input:** PR-Link oder PR-Nummer. Plattform aus Link oder `git remote -v`:
`github.com` → GitHub, `dev.azure.com` / `*.visualstudio.com` → Azure DevOps.

**GitHub** (`gh` CLI; GitHub MCP falls vorhanden):
- `gh pr view <n> --json title,body,author,baseRefName,headRefName,labels,state,mergeable`
- `gh pr diff <n>`
- Bestehende Kommentare: `gh pr view <n> --comments` + `gh api repos/<owner>/<repo>/pulls/<n>/comments`
  (inline). Nicht doppeln, Wichtiges ggf. verstärken.
- `gh` braucht die Sandbox aus (osxkeychain), sonst meldet `gh auth status` fälschlich "invalid".

**Azure DevOps** (`az repos` + git-diff): Org/Project/Repo aus Link oder Remote
(`git@ssh.dev.azure.com:v3/<org>/<project>/<repo>`; Projekt URL-decoden, `Web%20Platform` →
`Web Platform`). Bei Auth-Fehler den User um `az devops login` (PAT, Scope Code: Read) bitten.
- `az repos pr show --id <n> --org https://dev.azure.com/<org> -o json` → `title`, `description`,
  `sourceRefName`, `targetRefName`, `status`, `reviewers`, `workItemRefs`
- `git fetch origin && git diff origin/<target>...origin/<source>` (Refs ohne `refs/heads/`; bei
  grossem Diff zuerst `--stat`)
- Threads optional: `az devops invoke --area git --resource pullRequestThreads --route-parameters
  project="<project>" repositoryId=<repo> pullRequestId=<n> --org https://dev.azure.com/<org>`

**Beide:** `CLAUDE.md` (root + nested `**/CLAUDE.md`), falls nicht im Kontext — als harte Anforderung
lesen. Letzter Fallback: User um Diff-Paste bitten.

## 2. Kontext

Vor dem Review klären: Ziel des PR, Scope (Bugfix / Feature / Refactoring / Infra), betroffener Stack.

Optional bei grösseren PRs oder unklarem Test-Status: Branch lokal auschecken (`gh pr checkout <n>`
bzw. `git checkout <source>`) + `make test` / `make lint` — nur wenn der Aufwand Reviewwert bringt.

## 3. Prüfen

Nicht jede Kategorie trifft auf jeden PR zu. Fokus auf das Wesentliche.

- **🔴 CLAUDE.md / Projekt-Vorgaben** — Namens- und Coding-Konventionen, Architekturprinzipien,
  verbotene Patterns. Verstösse sind immer Blocker.
- **🔴 Security** — immer prüfen: Input-Validierung, Injection / XSS / CSRF, geloggte oder
  exponierte Secrets, AuthN/AuthZ, Dependencies mit bekannten Vulnerabilities.
- **🟠 Korrektheit** — löst der PR sein Problem? Bugs, falsche Annahmen, unbehandelte Edge-Cases,
  Error-Handling.
- **🟠 Performance** *(nur wenn relevant)* — N+1-Queries, unnötige Loops, blocking I/O, wiederholte
  teure Operationen, Leaks, ineffiziente Datenstrukturen.
- **🟡 Simplizität & Lesbarkeit** — unnötige Komplexität, Duplikate, nichtssagende Namen,
  "cleverer" Code, der schwer zu warten ist.
- **🟡 Best Practices** — Sprach- und Framework-Idiome, Anti-Patterns (God-Objects, Magic Numbers,
  tiefe Verschachtelung), fehlende oder sinnlose Tests, nötige Kommentare.
- **🔵 Situativ** — Breaking Changes, Migrations (rollback-fähig?), hardcodete Konfiguration,
  fehlende Observability.

## 4. Ausgeben

```
## PR Review: [Titel] (#Nummer)

**Zusammenfassung:** [1-2 Sätze: was der PR macht, Gesamteindruck]
**Empfehlung:** ✅ Approve / ❌ Request Changes

### 🔴 Blocker
### 🟠 Wichtig
### 🟡 Verbesserungsvorschläge
### 🔵 Nit-Picks
### ✅ Gut gelöst
```

- **Leere Sektionen weglassen.** Keine Platzhalter, kein "keine gefunden", kein Zwang, jede
  Kategorie zu befüllen.
- **Empfehlung:** 🔴 oder 🟠 vorhanden → Request Changes, sonst Approve.
- **Nummerierung:** Findings über alle Farben hinweg global durchnummeriert, damit in der Antwort
  eindeutig darauf verwiesen werden kann.
- **Finding-Form:** `Datei:Zeile` + ein Satz Befund + ein Satz Warum/Fix. Kein Nacherzählen des
  Diffs, keine Weichmacher ("könnte eventuell möglicherweise").
- **Ausserhalb des PR-Scope:** nur nennen, wenn es die Ticket-Schwelle des Projekts erfüllt (z. B.
  "When a finding earns a ticket" im Projekt-CLAUDE.md) — mit dem erfüllten Kriterium. Sonst weglassen.
- **✅ Gut gelöst** nur bei echt Verdientem und nur spezifisch — sonst weglassen.
- **Länge** an PR-Grösse: 1-Zeilen-Fix → wenige Zeilen. Komplexer PR ausführlicher, aber priorisiert.
- **Sprache:** Review-Output auf Deutsch, Code-Bezeichner im Original.

### Code-Snippets

Nur wenn sie die Weiterarbeit beschleunigen: nicht-offensichtlicher Fix, wiederholbares
Refactoring-Muster (einmal zeigen, Rest analog), spezifischer Security-Fix. Kein Snippet bei
trivialen oder rein stilistischen Punkten.

Format: `❌ vorher` / `✅ nachher`, Kommentarsyntax an die Dateisprache angepasst
(`#` Python/Shell, `//` JS/TS/Go/Java, `<!-- -->` HTML/Markdown).

**Nicht so:** "Diese Funktion könnte eventuell möglicherweise etwas performanter sein."
**So:** "Zeile 47: `getUserById()` in der Schleife → N+1. IDs sammeln, `getUsersByIds(ids)`."

## Prinzipien

1. **Ehrlichkeit vor Höflichkeit** — ein Review, der Probleme verschweigt, schadet dem Projekt.
2. **Scope respektieren** — keine Wunschliste für Dinge ausserhalb des PR.
3. **Priorisieren** — 3 klare Blocker sind hilfreicher als 20 Nit-Picks.
4. **Präzise** — konkrete Zeilen und Funktionen, nicht vage.
5. **Kontext beachten** — ein Quick-Fix hat andere Standards als Kern-Infrastruktur.
6. **Respektvoll** — Kritik am Code, nicht an der Person.
7. **CLAUDE.md ist Gesetz** — Verstösse dagegen sind immer Blocker.
