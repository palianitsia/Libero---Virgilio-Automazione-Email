// Background service worker
chrome.runtime.onInstalled.addListener(() => {
  console.log('Virgilio Cookie Extractor installato');
});

// Funzione per estrarre il cookie iolcmp-exp
async function getCookie(domain) {
  try {
    // Prova prima con il dominio specifico
    let cookies = await chrome.cookies.getAll({
      name: 'iolcmp-exp'
    });
    
    // Filtra i cookie per il dominio richiesto
    const filteredCookies = cookies.filter(cookie => 
      cookie.domain.includes(domain.replace('login.', ''))
    );
    
    if (filteredCookies && filteredCookies.length > 0) {
      // Restituisci il primo cookie trovato
      return filteredCookies[0].value;
    }
    return null;
  } catch (error) {
    console.error(`Errore nell'estrazione del cookie da ${domain}:`, error);
    return null;
  }
}

// Listener per le richieste dal popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCookies') {
    Promise.all([
      getCookie('virgilio.it'),
      getCookie('libero.it')
    ]).then(([virgilioCookie, liberoCookie]) => {
      sendResponse({
        virgilio: virgilioCookie || 'Non trovato',
        libero: liberoCookie || 'Non trovato'
      });
    }).catch(error => {
      sendResponse({
        virgilio: 'Errore',
        libero: 'Errore'
      });
    });
    return true; // Mantiene il canale di comunicazione aperto per la risposta asincrona
  }
});