from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import traceback

from lexer import Lexer
from parser import Parser
from generator import CodeGenerator
from interpreter import Interpreter

app = FastAPI(title="Sneaky Sneak Compiler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompileRequest(BaseModel):
    code: str

@app.get("/")
async def root():
    """Redirect root to home page."""
    return RedirectResponse(url="/sneakysneak-home")

@app.get("/sneakysneak-home")
async def home_page():
    """Serve the home page."""
    from fastapi.responses import FileResponse
    return FileResponse("home.html")

@app.get("/sneakysneak-compiler")
async def compiler_page():
    """Serve the compiler dashboard."""
    from fastapi.responses import FileResponse
    return FileResponse("index.html")

@app.post("/compile")
async def compile_code(request: CompileRequest):
    code = request.code
    
    try:
        # Lexical Analysis
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Assembly Code Generation
        generator = CodeGenerator(ast)
        assembly = generator.generate()
        
        # Execution / Interpretation
        interpreter = Interpreter(ast)
        output_txt = interpreter.run()
        
        return {
            "tokens": [token.to_dict() for token in tokens],
            "ast": ast.to_dict(),
            "assembly": assembly,
            "output": output_txt
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Serve static files (HTML, CSS, JS) — must be LAST so API routes take priority
app.mount("/", StaticFiles(directory="."), name="static")
