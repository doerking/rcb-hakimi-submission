## Role

You are an autonomous scientific research agent.

## Research Task

### Task Description

Reproduce the capabilities of a unified autoregressive framework that decouples visual encoding to perform both multimodal understanding (e.g., visual question answering, OCR) and visual generation (e.g., text-to-image generation) within a single Transformer architecture. Specifically:

1. **LaTeX formula recognition (understanding)**: Recognize the mathematical structure in `equation.png` and convert it into valid LaTeX code. This verifies the decoupled understanding encoder's precision for OCR and symbol recognition.

2. **Image generation**: Generate a high-quality image of Janus — the two-faced Roman god. The result should depict:
   - Left face: aged, with a blue/cold color palette
   - Right face: youthful, with a gold/warm color palette

3. **Meme semantic analysis (understanding)**: Analyze the "Swole Doge vs. Cheems" meme in `doge.png`. Extract the embedded text and interpret the visual metaphor of "Decoupling Visual Encoding" vs "Single Visual Encoder".

### Available Data Files
- `./data/equation.png` [sequence_data]: A mathematical equation image for OCR/formula-to-LaTeX recognition.
- `./data/doge.png` [sequence_data]: The "Swole Doge vs. Cheems" meme image with embedded text.

## Deliverables
1. `code/` — Python scripts for each task.
2. `outputs/` — Generated figure (`janus_gen_result.png`).
3. `report/report.md` — Analysis report with figures (mandatory).
