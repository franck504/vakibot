from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang=\"fr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>VakiBot</title>
  <style>
    :root{
      --bg:#f3f6fb;
      --bg2:#e8eef8;
      --panel:#ffffff;
      --ink:#0f172a;
      --muted:#475569;
      --line:#dbe4f0;
      --brand:#1d4ed8;
      --brand-2:#2563eb;
      --accent:#0f766e;
      --warn:#b45309;
      --danger:#b91c1c;
      --ok:#15803d;
      --chip:#eff6ff;
      --user:#dbeafe;
      --bot:#f8fafc;
      --shadow:0 8px 22px rgba(15,23,42,.08);
      --col-h:660px;
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0;
      color:var(--ink);
      font-family:"Source Sans 3","Segoe UI",sans-serif;
      background:
        linear-gradient(180deg,var(--bg),var(--bg2));
    }
    .app{max-width:1280px;margin:0 auto;padding:22px}
    .head{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      margin-bottom:14px;
    }
    .identity{display:flex;flex-direction:column;gap:4px}
    .brand{
      font-size:32px;
      line-height:1;
      font-weight:900;
      letter-spacing:.2px;
      color:#0b1733;
    }
    .subtitle{font-size:13px;color:var(--muted)}
    .status{
      border:1px solid var(--line);
      border-radius:999px;
      background:#fff;
      padding:8px 12px;
      font-size:12px;
      color:var(--muted);
      white-space:nowrap;
    }

    .layout{
      display:grid;
      grid-template-columns:minmax(0,2.2fr) minmax(320px,1fr);
      gap:14px;
      align-items:stretch;
    }
    .panel{
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:16px;
      box-shadow:var(--shadow);
      overflow:hidden;
    }
    .panel-head{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:8px;
      padding:12px 14px;
      border-bottom:1px solid var(--line);
      background:linear-gradient(180deg,#fff,#f8fbff);
    }
    .panel-title{
      font-size:14px;
      font-weight:800;
      text-transform:uppercase;
      letter-spacing:.6px;
      color:#1e3a8a;
    }
    .panel-body{padding:14px}

    .tip{
      display:flex;
      gap:8px;
      flex-wrap:wrap;
      margin-bottom:10px;
      color:var(--muted);
      font-size:12px;
    }
    .chip{
      display:inline-flex;
      align-items:center;
      border:1px solid #cddcf8;
      background:var(--chip);
      border-radius:999px;
      padding:2px 9px;
      font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
      font-size:11px;
      color:#1e3a8a;
    }

    #chat{
      min-height:0;
      max-height:none;
      overflow:auto;
      padding:10px;
      border:1px solid var(--line);
      border-radius:12px;
      background:#f9fbff;
    }
    .msg{
      margin:10px 0;
      padding:10px 12px;
      border-radius:12px;
      line-height:1.45;
      white-space:pre-wrap;
      border:1px solid transparent;
      font-size:15px;
    }
    .u{background:var(--user);border-color:#bfdbfe}
    .b{background:var(--bot);border-color:#e2e8f0}

    .row{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}
    .field{display:flex;flex-direction:column;gap:6px;min-width:0}
    .field label{font-size:12px;font-weight:700;color:var(--muted)}
    .grow{flex:1}
    .w120{width:120px}
    .w100{width:100px}

    input,textarea,button{
      font:inherit;
      border-radius:10px;
      border:1px solid var(--line);
      padding:10px 11px;
      background:#fff;
      color:var(--ink);
    }
    input:focus,textarea:focus{
      outline:none;
      border-color:#93c5fd;
      box-shadow:0 0 0 3px rgba(59,130,246,.15);
    }
    textarea{width:100%;min-height:82px;resize:vertical}

    .btn{
      background:var(--brand);
      color:#fff;
      border:none;
      cursor:pointer;
      font-weight:700;
    }
    .btn:hover{background:var(--brand-2)}
    .btn-sub{
      background:#fff;
      color:#0f172a;
      border:1px solid var(--line);
      cursor:pointer;
      font-weight:600;
    }
    .btn-sub:hover{background:#f8fafc}
    .btn-danger{background:var(--danger);color:#fff;border:none;cursor:pointer}
    .btn-danger:hover{background:#991b1b}

    .meta{font-size:12px;color:var(--muted);margin-bottom:5px}
    .small{font-size:12px;color:var(--muted)}
    .ok{color:var(--ok);font-weight:700}

    .stack{display:grid;gap:14px;height:var(--col-h);grid-template-rows:min-content minmax(0,1fr);overflow:hidden}
    .stack > *{min-height:0}
    #sources{height:100%;max-height:none;overflow:auto;display:grid;gap:8px}
    .chat-panel{height:var(--col-h);display:flex;flex-direction:column}
    .chat-panel .panel-body{display:flex;flex-direction:column;flex:1;min-height:0}
    .sources-panel{display:flex;flex-direction:column;min-height:0;overflow:hidden}
    .sources-panel .panel-body{flex:1;min-height:0}
    .src{
      border:1px solid var(--line);
      border-radius:10px;
      background:#fff;
      padding:9px;
    }

    @media (max-width:1000px){
      .layout{grid-template-columns:1fr}
      .chat-panel{height:auto}
      .stack{height:auto;grid-template-rows:auto auto}
      #chat{min-height:260px;max-height:360px}
      .head{align-items:flex-start;flex-direction:column}
      .status{white-space:normal}
      #sources{max-height:280px;height:auto}
    }
  </style>
</head>
<body>
  <div class=\"app\">
    <header class=\"head\">
      <div class=\"identity\">
        <div class=\"brand\">VakiBot</div>
        <div class=\"subtitle\">Assistant juridique documentaire</div>
      </div>
      <div class=\"status\" id=\"status\">API status: checking...</div>
    </header>

    <main class=\"layout\">
      <section class=\"panel chat-panel\">
        <div class=\"panel-head\">
          <div class=\"panel-title\">Chat</div>
        </div>
        <div class=\"panel-body\">
          <div class=\"tip\">
            <span>Conseil:</span>
            <span class=\"chip\">domain=loi</span>
            <span class=\"chip\">lang=fr</span>
            <span class=\"chip\">top_k=8..12</span>
          </div>

          <div id=\"chat\"></div>

          <div class=\"row\">
            <textarea id=\"question\" placeholder=\"Ex: Quel est le délai de prescription pour un délit ?\"></textarea>
          </div>

          <div class=\"row\">
            <div class=\"field grow\">
              <label for=\"qDomain\">Domaine (optionnel)</label>
              <input id=\"qDomain\" placeholder=\"loi\" />
            </div>
            <div class=\"field w120\">
              <label for=\"qLang\">Langue</label>
              <input id=\"qLang\" placeholder=\"fr\" />
            </div>
            <div class=\"field w100\">
              <label for=\"qTopK\">Top K</label>
              <input id=\"qTopK\" type=\"number\" min=\"1\" max=\"20\" value=\"8\" />
            </div>
          </div>

          <div class=\"row\">
            <button id=\"askBtn\" class=\"btn\">Envoyer</button>
            <button id=\"clearHistoryBtn\" class=\"btn-sub\">Vider historique</button>
            <button id=\"loadSourcesBtn\" class=\"btn-sub\">Rafraichir sources</button>
          </div>
        </div>
      </section>

      <aside class=\"stack\">
        <section class=\"panel ingestion-panel\">
          <div class=\"panel-head\"><div class=\"panel-title\">Ingestion</div></div>
          <div class=\"panel-body\">
            <input id=\"files\" type=\"file\" multiple />
            <div class=\"row\">
              <div class=\"field grow\">
                <label for=\"domain\">Domaine</label>
                <input id=\"domain\" placeholder=\"loi\" />
              </div>
              <div class=\"field w120\">
                <label for=\"lang\">Langue</label>
                <input id=\"lang\" placeholder=\"fr\" />
              </div>
            </div>
            <div class=\"row\"><button id=\"ingestBtn\" class=\"btn\">Indexer</button></div>
            <div id=\"ingestResult\" class=\"small\" style=\"margin-top:8px\"></div>
          </div>
        </section>

        <section class=\"panel sources-panel\">
          <div class=\"panel-head\"><div class=\"panel-title\">Sources</div></div>
          <div class=\"panel-body\"><div id=\"sources\"></div></div>
        </section>
      </aside>
    </main>
  </div>

<script>
const chat=document.getElementById('chat'),questionEl=document.getElementById('question'),statusEl=document.getElementById('status'),ingestResult=document.getElementById('ingestResult'),sourcesEl=document.getElementById('sources');
const HISTORY_KEY='vakibot_chat_history_v1';
const saveHistory=i=>localStorage.setItem(HISTORY_KEY,JSON.stringify(i));
const loadHistory=()=>{try{return JSON.parse(localStorage.getItem(HISTORY_KEY)||'[]')}catch{return[]}};
function renderHistory(){chat.innerHTML='';for(const m of loadHistory())addMsg(m.text,m.role,false)}
function pushHistory(text,role){const items=loadHistory();items.push({text,role,ts:Date.now()});saveHistory(items)}
function addMsg(txt,cls,persist=true){const d=document.createElement('div');d.className=`msg ${cls}`;d.textContent=txt;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;if(persist)pushHistory(txt,cls)}
async function checkHealth(){try{const res=await fetch('/health');const j=await res.json();statusEl.textContent=`API status: ${j.status} | ${j.environment}`}catch{statusEl.textContent='API status: offline'}}
async function deleteDoc(docId){if(!confirm(`Supprimer le document ${docId} ?`))return;const res=await fetch(`/documents/${docId}`,{method:'DELETE'});const j=await res.json();if(!res.ok){alert(j.detail||'suppression impossible');return}await loadSources()}
async function loadSources(){const res=await fetch('/sources?limit=50');const j=await res.json();sourcesEl.innerHTML='';for(const s of (j.sources||[])){const card=document.createElement('div');card.className='src';card.innerHTML=`<div class='meta'>${s.filename} · doc=${s.doc_id.slice(0,8)} · chunk=${s.chunk_index} · ${s.domain}/${s.lang}</div><div>${s.excerpt}</div><div class='row'><button class='btn-danger' data-doc='${s.doc_id}'>Supprimer doc</button></div>`;sourcesEl.appendChild(card)}for(const btn of sourcesEl.querySelectorAll('button[data-doc]'))btn.onclick=()=>deleteDoc(btn.getAttribute('data-doc'))}

document.getElementById('askBtn').onclick=async()=>{const q=questionEl.value.trim();if(!q)return;addMsg(q,'u');questionEl.value='';const topK=parseInt(document.getElementById('qTopK').value||'8',10),domain=document.getElementById('qDomain').value.trim().toLowerCase(),lang=document.getElementById('qLang').value.trim().toLowerCase();try{const payload={question:q,top_k:topK};if(domain)payload.domain=domain;if(lang)payload.lang=lang;const res=await fetch('/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const j=await res.json();if(!res.ok)addMsg(`Erreur: ${j.detail||'query failed'}`,'b');else{const prefix=(j.confidence==='low')?`[Confiance faible | score moyen: ${(j.avg_score||0).toFixed(2)}]\n`:'';addMsg(`${prefix}${j.answer}`,'b');await loadSources()}}catch{addMsg('Erreur reseau','b')}};

document.getElementById('ingestBtn').onclick=async()=>{const files=document.getElementById('files').files;if(!files.length){ingestResult.textContent='Veuillez selectionner au moins un fichier.';return}const fd=new FormData();for(const f of files)fd.append('files',f);const domain=document.getElementById('domain').value.trim().toLowerCase(),lang=document.getElementById('lang').value.trim().toLowerCase();if(domain)fd.append('domain',domain);if(lang)fd.append('lang',lang);ingestResult.textContent='Indexation en cours...';const res=await fetch('/ingest',{method:'POST',body:fd});const j=await res.json();if(!res.ok){ingestResult.textContent=`Erreur ingestion: ${j.detail||j.error||'inconnue'}`;return;}ingestResult.innerHTML=`<span class=\"ok\">Indexation terminee.</span> status=${j.status}, docs=${j.documents_indexed}, chunks=${j.chunks_indexed}, total_chunks=${j.total_chunks}, errors=${(j.errors||[]).length}`;await loadSources()};

document.getElementById('clearHistoryBtn').onclick=()=>{saveHistory([]);renderHistory()};
document.getElementById('loadSourcesBtn').onclick=loadSources;
questionEl.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')document.getElementById('askBtn').click()});
checkHealth();renderHistory();loadSources();
</script>
</body></html>"""
