## PlantUML diagrams

Files in this folder are ready to render with the **PlantUML** extension.

### Diagrams included
- `01-component.puml`: high-level architecture/layers
- `02-domain-class.puml`: DB entities + foreign-key relationships
- `03-seq-auth.puml`: signup + login flow
- `04-seq-activity.puml`: click, order, rate flows
- `05-seq-recommendations.puml`: recommendation request flow

### Render in Cursor / VS Code (PlantUML extension)
1. Install the extension: **PlantUML** (publisher: *jebbs*).
2. Open any `.puml` file in this folder.
3. Use the command palette:
   - **PlantUML: Preview Current Diagram** (live preview)
   - **PlantUML: Export Current Diagram** (PNG/SVG/PDF)

### If preview/export fails on Windows
The extension needs a renderer.

Option A (recommended): **Graphviz + local PlantUML**
- Install Graphviz and ensure `dot` is on PATH.
- Ensure Java is installed (JRE/JDK) so PlantUML can run.

Option B: **Use the PlantUML server**
- Set setting `plantuml.render` to `PlantUMLServer`
- Set `plantuml.server` to a PlantUML server URL

