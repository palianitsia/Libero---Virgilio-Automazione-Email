// Gestione del popup

// Carica il tema salvato
async function loadTheme() {
  const result = await chrome.storage.local.get(['theme']);
  const theme = result.theme || 'system';
  applyTheme(theme);
  return theme;
}

// Applica il tema
function applyTheme(theme) {
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
}

// Salva il tema
async function saveTheme(theme) {
  await chrome.storage.local.set({ theme: theme });
}

// Ottieni il prossimo tema
function getNextTheme(currentTheme) {
  const themes = ['light', 'dark', 'system'];
  const currentIndex = themes.indexOf(currentTheme);
  return themes[(currentIndex + 1) % themes.length];
}

// Copia testo negli appunti
async function copyToClipboard(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    
    // Feedback visivo
    const originalText = button.textContent;
    button.classList.add('copied');
    
    setTimeout(() => {
      button.classList.remove('copied');
    }, 1500);
    
  } catch (error) {
    console.error('Errore nella copia:', error);
    // Fallback per browser più vecchi
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    button.classList.add('copied');
    setTimeout(() => {
      button.classList.remove('copied');
    }, 1500);
  }
}

// Estrai i cookie
async function extractCookies() {
  const virgilioOutput = document.getElementById('virgilioOutput');
  const liberoOutput = document.getElementById('liberoOutput');
  
  virgilioOutput.textContent = 'Caricamento...';
  liberoOutput.textContent = 'Caricamento...';
  
  // Rimuovi event handler precedenti
  virgilioOutput.onclick = null;
  liberoOutput.onclick = null;
  
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getCookies' });
    
    const virgilioValue = response.virgilio;
    const liberoValue = response.libero;
    
    virgilioOutput.textContent = virgilioValue;
    liberoOutput.textContent = liberoValue;
    
    // Aggiungi click handler solo se il cookie è stato trovato
    if (virgilioValue !== 'Non trovato' && virgilioValue !== 'Errore') {
      virgilioOutput.onclick = () => copyToClipboard(virgilioValue, virgilioOutput);
    }
    
    if (liberoValue !== 'Non trovato' && liberoValue !== 'Errore') {
      liberoOutput.onclick = () => copyToClipboard(liberoValue, liberoOutput);
    }
    
  } catch (error) {
    virgilioOutput.textContent = 'Errore: ' + error.message;
    liberoOutput.textContent = 'Errore: ' + error.message;
  }
}

// Inizializzazione
document.addEventListener('DOMContentLoaded', async () => {
  // Carica tema
  const currentTheme = await loadTheme();
  
  // Gestione cambio tema
  const themeToggle = document.getElementById('themeToggle');
  themeToggle.addEventListener('click', async () => {
    const newTheme = getNextTheme(currentTheme);
    await saveTheme(newTheme);
    applyTheme(newTheme);
  });
  
  // Gestione refresh
  const refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.addEventListener('click', extractCookies);
  
  // Estrai cookie al caricamento
  extractCookies();
  
  // Ascolta cambiamenti del tema di sistema
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', async () => {
    const result = await chrome.storage.local.get(['theme']);
    if (result.theme === 'system') {
      applyTheme('system');
    }
  });
});