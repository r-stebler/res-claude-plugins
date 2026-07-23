---
name: git-pr-review
description: Führt einen gründlichen, ehrlichen und kritischen Code-Review eines Pull Requests durch – GitHub oder Azure DevOps. Nutze diesen Skill immer wenn der User einen PR reviewen, prüfen, analysieren oder begutachten möchte – egal ob mit PR-Link, PR-Nummer oder Beschreibung wie "schau dir PR #42 an", "review meinen PR", "was hältst du von diesem PR" oder "kannst du den PR checken". Auch bei Fragen wie "ist der PR merge-ready?" oder "gibt es Probleme mit dem PR?" direkt anwenden.
compatibility: "GitHub: `gh` CLI (bzw. GitHub MCP). Azure DevOps: `az repos` + git-diff. Plattform wird aus PR-Link/Remote erkannt."
---

# PR Review Skill

Führe einen **ehrlichen, kritischen und konstruktiven** Code-Review durch. Kein oberflächliches Loben – echte Probleme klar benennen, Prioritäten setzen, Verbesserungen konkret vorschlagen.

---

## Schritt 1: PR-Daten laden

**Input:** PR-Link oder PR-Nummer + Repo-Kontext.

**Plattform erkennen** – aus dem PR-Link oder `git remote -v`:
- `github.com` → **GitHub-Pfad**
- `dev.azure.com` / `*.visualstudio.com` → **Azure-DevOps-Pfad**

### GitHub-Pfad (`gh` CLI, in jedem GitHub-Repo verfügbar)
1. **PR-Metadaten** – `gh pr view <n> --json title,body,author,baseRefName,headRefName,labels,state,mergeable`
2. **Diff** – `gh pr diff <n>`
3. **Bestehende Review-Kommentare** – `gh pr view <n> --comments` und `gh api repos/<owner>/<repo>/pulls/<n>/comments` (Inline-Kommentare). Doppelungen vermeiden, wichtige Befunde ggf. verstärken.

Alternative: GitHub MCP falls vorhanden.

### Azure-DevOps-Pfad (`az repos` + git-diff)
Org/Project/Repo aus dem PR-Link oder `git remote -v` auflösen (SSH `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>`; Projekt **URL-decoden**, z. B. `Web%20Platform` → `Web Platform`). Nutzt die bestehende `az`-Session; bei Auth-Fehler den User bitten, `az devops login` (PAT, Scope Code: Read) auszuführen.
1. **PR-Metadaten** – `az repos pr show --id <n> --org https://dev.azure.com/<org> -o json` → `title`, `description`, `sourceRefName`, `targetRefName`, `status`, `reviewers`, `workItemRefs`.
2. **Diff** – Branch-Namen aus den Refs ableiten (ohne `refs/heads/`), dann `git fetch origin` und `git diff origin/<target>...origin/<source>` (Drei-Punkt: die im Source neu hinzugekommenen Änderungen). Bei großem Diff zuerst `--stat` für den Überblick.
3. **Bestehende Kommentare/Threads** *(optional)* – `az devops invoke --area git --resource pullRequestThreads --route-parameters project="<project>" repositoryId=<repo> pullRequestId=<n> --org https://dev.azure.com/<org>` (REST); sonst kurzer Web-UI-Verweis.

### Gemeinsam
4. **CLAUDE.md** – falls noch nicht im Kontext: Root und ggf. nested `**/CLAUDE.md` lesen. Als harte Anforderung behandeln.

**Fallback** (beide Pfade scheitern): User um Diff-Paste bitten.

---

## Schritt 2: Kontext verstehen

Bevor du reviewst, verschaffe dir ein klares Bild:
- **Was soll dieser PR erreichen?** (aus Beschreibung + Diff ableiten)
- **Wie groß ist der Scope?** (Bugfix, Feature, Refactoring, Infrastruktur?)
- **Welches Tech-Stack / welche Sprachen** sind betroffen?
- **Gibt es eine CLAUDE.md?** → Inhalt lesen und als harte Anforderung behandeln

**Optional: lokale Verifikation** — bei größeren PRs oder wenn Tests/Lint-Status unklar:
Source-Branch lokal auschecken (GitHub: `gh pr checkout <n>`; Azure DevOps: `git fetch origin && git checkout <source-branch>`) und z. B. `mvn test` / `make test` / `make lint` laufen lassen. Nur wenn der Aufwand den Reviewwert rechtfertigt — bei trivialen PRs überspringen.

---

## Schritt 3: Review durchführen

Analysiere den PR nach folgenden Kategorien. **Nicht jede Kategorie ist bei jedem PR relevant** – fokussiere dich auf das Wesentliche.

### 🔴 CLAUDE.md / Projekt-Vorgaben
*(Nur wenn CLAUDE.md existiert – sonst überspringen)*
- Werden alle expliziten Vorgaben eingehalten? (Namenskonventionen, Architekturprinzipien, verbotene Patterns, Coding-Standards)
- Gibt es direkte Verstösse? → Diese sind **Blocker**, klar als solche markieren

### 🟠 Korrektheit & Logik
- Löst der PR das Problem, das er lösen soll?
- Gibt es offensichtliche Bugs, falsche Annahmen, Edge-Cases die nicht behandelt werden?
- Sind Error-Handling und Grenzfälle berücksichtigt?

### 🟡 Simplizität, Redundanz & Lesbarkeit
- Gibt es unnötig komplexen Code, der einfacher gelöst werden könnte?
- Wird Code dupliziert, der bereits existiert oder abstrahiert werden sollte?
- Sind Variablen- und Funktionsnamen aussagekräftig?
- Ist die Logik nachvollziehbar ohne intensive Analyse?
- Gibt es "clever" geschriebenen Code, der schwer zu warten ist?

### 🟡 Best Practices & Common Patterns
- Werden etablierte Patterns der Sprache/des Frameworks eingehalten?
- Werden Anti-Patterns verwendet (God-Objects, Magic Numbers, tief verschachtelte Logik)?
- Sind Tests vorhanden und sinnvoll? Fehlen kritische Test-Cases?
- Sind Kommentare und Dokumentation wo nötig vorhanden?

### 🟠 Performance
*(Nur wenn relevant – nicht bei jedem CRUD-Endpoint nötig)*
- Gibt es offensichtliche Performance-Probleme? (N+1 Queries, unnötige Loops, blocking I/O)
- Werden teure Operationen unnötig wiederholt?
- Gibt es Memory-Leaks oder ineffiziente Datenstrukturen?

### 🔴 Security
*(Immer prüfen, auch wenn nichts auffällt – explizit "keine Probleme gefunden" vermerken)*
- Werden User-Inputs validiert und sanitisiert?
- Gibt es SQL-Injection, XSS, CSRF oder ähnliche Angriffsvektoren?
- Werden Secrets/Credentials versehentlich geloggt oder exponiert?
- Sind Berechtigungen und Authentifizierung korrekt implementiert?
- Werden Dependencies mit bekannten Vulnerabilities eingeführt?

### 🔵 Weitere Aspekte (situativ)
- **Breaking Changes:** Werden bestehende APIs/Interfaces inkompatibel verändert?
- **Migrations:** Falls DB-Migrationen enthalten – sind sie rollback-fähig?
- **Konfiguration:** Hardcoded Werte die konfigurierbar sein sollten?
- **Observability:** Fehlen sinnvolle Logs, Metrics oder Tracing?

---

## Schritt 4: Review ausgeben

### Format

```
## PR Review: [Titel] (#Nummer)

**Zusammenfassung:** [2-3 Sätze: Was macht der PR, Gesamteindruck]

**Empfehlung:** ✅ Approve / ❌ Request Changes
(Mapping: Existieren 🔴 Blocker oder 🟠 Wichtige Anmerkungen → Request Changes. Sonst Approve, ggf. mit optionalen 🟡/🔵 Hinweisen.)

---

### 🔴 Blocker (müssen vor Merge behoben werden)
[Falls keine: "Keine Blocker gefunden."]
[Security-Blocker hier einsortieren — keine separate Security-Sektion oben drüber.]

### 🟠 Wichtige Anmerkungen (sollten behoben werden)
[Falls keine: "Keine wichtigen Anmerkungen."]

### 🟡 Verbesserungsvorschläge (optional, aber empfohlen)
[Konkrete Vorschläge mit Begründung]

### 🔵 Kleinigkeiten / Nit-Picks
[Nur wenn relevant, nicht übertreiben]

### ✅ Was gut gelöst ist
[Ehrliches Lob – nur wenn wirklich verdient]

---
### Security-Check (Pflicht-Vermerk)
[Falls Security-Findings existieren: in den Prio-Sektionen oben einsortiert; hier nur kurzer Verweis.
 Falls nichts gefunden: "Keine Sicherheitsprobleme gefunden."]
```

**Output-Länge:** An PR-Größe anpassen. Bei trivialen PRs (1-Zeilen-Fix, Doc-Update) leere Sektionen weglassen — kein Zwang, jede Kategorie zu befüllen. Bei komplexen PRs ausführlicher, aber immer priorisiert.

**Nummerierung:** Alle Findings + die damit verbundenen verbesserungsvorschläge sind über alle Farben hinweg global durchnummeriert, so dass in der Antwort eindeutig auf sie verwiesen werden kann. 

### Sprache
Der gesamte Review-Output erfolgt auf **Deutsch** – unabhängig von der Sprache des Codes oder der PR-Beschreibung. Code-Bezeichner (Variablen, Funktionsnamen, Dateinamen) werden natürlich im Original belassen.

### Code-Snippets im Review
Füge Snippets **gezielt** ein – nur wenn sie die Weiterarbeit direkt effizienter machen:

**Snippet einfügen wenn:**
- Der Fix nicht offensichtlich ist und ein Beispiel die Umsetzung wesentlich beschleunigt
- Ein Refactoring-Muster gezeigt werden soll das sich wiederholt (einmal zeigen, Rest analog)
- Eine Security-Schwachstelle einen spezifischen Fix erfordert

**Kein Snippet nötig wenn:**
- Der Fix trivial und klar beschrieben ist ("Variablenname `x` → `userId` umbenennen")
- Es nur um Stil geht der eindeutig aus dem Kontext hervorgeht

**Format:** Immer mit `❌ vorher` / `✅ nachher` kommentieren für schnelle Orientierung. Kommentar-Syntax an die Sprache der Datei anpassen (`# ❌ vorher` für Python/Shell, `// ❌ vorher` für JS/TS/Go/Java, `<!-- ❌ vorher -->` für HTML/Markdown).

### Tonalität & Qualität

- **Direkt und ehrlich** – kein falsches Loben, keine Weichspüler
- **Konstruktiv** – Probleme benennen UND konkrete Lösungen vorschlagen
- **Priorisiert** – Blocker klar von Nice-to-haves trennen
- **Präzise** – Auf konkrete Zeilen/Funktionen verweisen, nicht vage
- **Respektvoll** – Kritik am Code, nicht an der Person

### Beispiel für gutes Feedback (nicht so):
> ❌ "Diese Funktion könnte eventuell möglicherweise etwas performanter sein."

### Beispiel für gutes Feedback (so):
> ✅ "Zeile 47: `getUserById()` wird in einer Schleife aufgerufen → N+1 Query-Problem. IDs sammeln und mit `getUsersByIds(ids)` in einem Query laden."

---

## Wichtige Prinzipien

1. **Ehrlichkeit vor Höflichkeit** – Ein Review der Probleme verschweigt schadet dem Projekt
2. **Scope respektieren** – Keine Wunschliste für Dinge die ausserhalb des PR-Scope sind
3. **Prioritäten setzen** – 3 klare Blocker sind hilfreicher als 20 Nit-Picks
4. **Kontext beachten** – Ein Quick-Fix hat andere Standards als Kern-Infrastruktur
5. **CLAUDE.md ist Gesetz** – Verstösse dagegen sind immer Blocker
