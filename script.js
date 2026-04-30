// ===== Example Code Snippets =====
const EXAMPLES = {
    "-- Select Example --": "",
    "Arithmetic": `x = 10 + 5 * 2
y = (x - 3) ** 2
z = y // 10 % 7
print(x)
print(y)
print(z)`,
    "If / Elif / Else": `score = 85
if score >= 90:
    print('A')
elif score >= 80:
    print('B')
elif score >= 70:
    print('C')
else:
    print('F')`,
    "While Loop": `i = 1
total = 0
while i <= 10:
    total = total + i
    i = i + 1
print(total)`,
    "For Loop": `for i in range(1, 6):
    print(i * i)`,
    "Nested Loops": `for i in range(1, 4):
    for j in range(1, 4):
        print(i * j)`,
    "Logical Operators": `x = 15
if x > 10 and x < 20:
    print('in range')
if x == 5 or x == 15:
    print('match')
if not x == 0:
    print('not zero')`,
    "Fibonacci": `a = 0
b = 1
for i in range(10):
    print(a)
    temp = b
    b = a + b
    a = temp`,
    "Factorial": `n = 6
result = 1
for i in range(1, 7):
    result = result * i
print(result)`,
};

function loadExample() {
    const select = document.getElementById('exampleSelect');
    const textarea = document.getElementById('codeInput');
    const selectedCode = EXAMPLES[select.value];
    if (selectedCode !== undefined) {
        textarea.value = selectedCode;
        updateLineNumbers();
    }
}

// ===== Line Numbers =====
function updateLineNumbers() {
    const textarea = document.getElementById('codeInput');
    const lineNumbers = document.getElementById('lineNumbers');
    if (!textarea || !lineNumbers) return;
    
    const lines = textarea.value.split('\n');
    const count = lines.length;
    let html = '';
    for (let i = 1; i <= count; i++) {
        html += i + '\n';
    }
    lineNumbers.textContent = html;
    
    // Sync scroll position
    lineNumbers.scrollTop = textarea.scrollTop;
}

function syncScroll() {
    const textarea = document.getElementById('codeInput');
    const lineNumbers = document.getElementById('lineNumbers');
    if (lineNumbers && textarea) {
        lineNumbers.scrollTop = textarea.scrollTop;
    }
}

// ===== Copy to Clipboard =====
function copyOutput(elementId) {
    const el = document.getElementById(elementId);
    const text = el.textContent || el.innerText;
    
    const copyFn = () => {
        const btn = el.closest('.output-panel').querySelector('.copy-btn');
        if (btn) {
            btn.classList.add('copied');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = originalHTML;
            }, 1500);
        }
    };
    
    navigator.clipboard.writeText(text).then(copyFn).catch(() => {
        // Fallback for file:// protocol
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        copyFn();
    });
}

// ===== Compile Code =====
async function compileCode() {
    const code = document.getElementById('codeInput').value;
    const lexerOutput = document.getElementById('lexerOutput');
    const parserOutput = document.getElementById('parserOutput');
    const assemblyOutput = document.getElementById('assemblyOutput');
    const executionOutput = document.getElementById('executionOutput');
    const btn = document.getElementById('compileBtn');

    // Loading state
    btn.disabled = true;
    btn.querySelector('span').innerHTML = `
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        COMPILING...`;

    const loadingHTML = '<span class="text-slate-500 italic">Processing...</span>';
    lexerOutput.innerHTML = loadingHTML;
    parserOutput.innerHTML = loadingHTML;
    assemblyOutput.innerHTML = loadingHTML;
    executionOutput.innerHTML = loadingHTML;

    try {
        const response = await fetch('http://127.0.0.1:8000/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        if (!response.ok) {
            let errorMsg = `HTTP error! status: ${response.status}`;
            try {
                const errData = await response.json();
                if (errData.detail) errorMsg = errData.detail;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        const data = await response.json();

        lexerOutput.textContent = data.tokens ? JSON.stringify(data.tokens, null, 2) : "[]";
        parserOutput.textContent = data.ast ? JSON.stringify(data.ast, null, 2) : "{}";
        assemblyOutput.textContent = data.assembly || "No assembly generated.";
        executionOutput.textContent = data.output !== undefined && data.output !== "" ? data.output : "No output generated.";
        
        executionOutput.classList.remove("text-red-400");
        executionOutput.classList.add("text-emerald-300");

    } catch (error) {
        console.error("Compilation error:", error);
        const errorText = error.message;
        
        lexerOutput.textContent = "Compilation halted.";
        parserOutput.textContent = "Compilation halted.";
        assemblyOutput.textContent = "Compilation halted.";

        executionOutput.classList.remove("text-emerald-300");
        executionOutput.classList.add("text-red-400");
        executionOutput.textContent = "ERROR: " + errorText;
    }

    // Restore button
    btn.disabled = false;
    btn.querySelector('span').innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        RUN COMPILER`;
}

// ===== Keyboard Shortcuts & Init =====
document.addEventListener('DOMContentLoaded', () => {
    const codeInput = document.getElementById('codeInput');
    if (codeInput) {
        // Init line numbers
        updateLineNumbers();
        
        codeInput.addEventListener('input', updateLineNumbers);
        codeInput.addEventListener('scroll', syncScroll);
        codeInput.addEventListener('keydown', (e) => {
            // Ctrl+Enter to compile
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                compileCode();
            }
            // Tab key inserts 4 spaces
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = codeInput.selectionStart;
                const end = codeInput.selectionEnd;
                codeInput.value = codeInput.value.substring(0, start) + '    ' + codeInput.value.substring(end);
                codeInput.selectionStart = codeInput.selectionEnd = start + 4;
                updateLineNumbers();
            }
        });
    }
});