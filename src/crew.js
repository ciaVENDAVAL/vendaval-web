// VENDAVAL crew register: month + initials -> a job on board and a sea name.
// Spanish data is built in; other languages load window.CREW_DATA from assets/crew-data/<lang>.js
(function () {
/*DATA*/
const MESES = [
  { n: "Enero", e: "invierno", t: [
    "Almirante|Almiranta de la Sopa Caliente",
    "Descongelador|Descongeladora de Anclas",
    "Cortauñas Oficial de Dedos Congelados",
    "Calentador|Calentadora de Timones",
    "Vigía del Bacalao Dormido" ] },
  { n: "Febrero", e: "invierno", t: [
    "Capitán|Capitana de Tormentas de Carnaval",
    "Frotador|Frotadora de Cubiertas Resbaladizas",
    "Secador|Secadora de Calcetines Marineros",
    "Contador|Contadora de Olas Gigantes",
    "Cocinero|Cocinera de Estofado Antimareo" ] },
  { n: "Marzo", e: "primavera", t: [
    "Pintor|Pintora de Cascos Recién Despiertos",
    "Despertador|Despertadora de Sirenas",
    "Grumete Superior de Telarañas",
    "Pulidor|Pulidora de Bronces Oxidados",
    "Barrendero|Barrendera de Algas Marchitas" ] },
  { n: "Abril", e: "primavera", t: [
    "Contramaestre|Contramaestra de la Lluvia Fina",
    "Friegasuelos Oficial de Cubierta",
    "Sembrador|Sembradora de Mejillones",
    "Peinador|Peinadora de Medusas",
    "Piloto|Pilota de Barcos de Papel" ] },
  { n: "Mayo", e: "primavera", t: [
    "Capitán|Capitana de Regatas Florales",
    "Cocinero|Cocinera de Paella Marinera",
    "Lustrador|Lustradora de Botones de Almirante",
    "Afinador|Afinadora de Sirenas Desafinadas",
    "Timonel a Media Jornada" ] },
  { n: "Junio", e: "verano", t: [
    "Vigilante del Bronceado Perfecto",
    "Almirante|Almiranta de Flotadores",
    "Untador|Untadora de Crema Solar a Delfines",
    "Heladero|Heladera de Cubierta",
    "Salvador|Salvadora de Sombrillas" ] },
  { n: "Julio", e: "verano", t: [
    "Capitán|Capitana de Chanclas",
    "Pescador|Pescadora de Siestas",
    "Hinchador|Hinchadora de Colchonetas",
    "Pulidor|Pulidora de Caracolas",
    "Cocinero|Cocinera de Gazpacho Flotante" ] },
  { n: "Agosto", e: "verano", t: [
    "Abanicador|Abanicadora de Velas Quietas",
    "Almirante|Almiranta de la Siesta Naval",
    "Cazador|Cazadora de Brisas Perdidas",
    "Contramaestre|Contramaestra de la Calma Chicha",
    "Catador|Catadora de Sandía Sumergida" ] },
  { n: "Septiembre", e: "otoño", t: [
    "Remendador|Remendadora de Redes Rotas",
    "Capitán|Capitana de la Vendimia Marítima",
    "Recolector|Recolectora de Hojas Flotantes",
    "Afilador|Afiladora de Anzuelos",
    "Tostador|Tostadora de Castañas en Cubierta" ] },
  { n: "Octubre", e: "otoño", t: [
    "Vigía de Huracanes Elegantes",
    "Almirante|Almiranta de las Nieblas",
    "Sujetador|Sujetadora de Sombreros Voladores",
    "Encendedor|Encendedora de Faros Perezosos",
    "Domador|Domadora de Olas Otoñales" ] },
  { n: "Noviembre", e: "otoño", t: [
    "Capitán|Capitana de Paraguas Náuticos",
    "Calafateador|Calafateadora de Goteras",
    "Guardián|Guardiana de Gaviotas Mojadas",
    "Cocinero|Cocinera de Caldo de Niebla",
    "Contramaestre|Contramaestra de Bufandas" ] },
  { n: "Diciembre", e: "invierno", t: [
    "Almirante|Almiranta del Turrón Naval",
    "Decorador|Decoradora de Mástiles Navideños",
    "Capitán|Capitana de la Nochebuena Flotante",
    "Envolvedor|Envolvedora de Regalos para Krakens",
    "Cortauñas Real de Pies Piratas" ] }
];

/* Sustantivos del mar. Formato: palabra:género (m o f) */
const NOMBRES_RAW = {
  A: "ancla:f, atún:m, alga:f, almeja:f, anémona:f, anguila:f, arenque:m, albatros:m, aleta:f, arrecife:m, astillero:m, arpón:m, amarre:m, alcatraz:m, anchoa:f, atolón:m, aguamala:f, acantilado:m, aparejo:m, abordaje:m, abadejo:m, aguja:f",
  B: "ballena:f, barco:m, bergantín:m, bacalao:m, boya:f, brújula:f, barracuda:f, babor:m, bahía:f, balandro:m, buque:m, besugo:m, berberecho:m, bogavante:m, brisa:f, bitácora:f, bauprés:m, bajío:m, boquerón:m, bonito:m, bote:m, batiscafo:m, buzo:m",
  C: "calamar:m, cangrejo:m, carabela:f, caracola:f, corsario:m, camarón:m, cormorán:m, cachalote:m, coral:m, corbeta:f, cabo:m, catamarán:m, concha:f, caballito de mar:m, cubierta:f, cala:f, corriente:f, cazón:m, congrio:m, chipirón:m, centolla:f, camarote:m, cabrilla:f, cetáceo:m",
  D: "delfín:m, dorada:f, dársena:f, dragaminas:m, dentón:m, dique:m, doblón:m, deriva:f, damisela:f, dugongo:m, dorado:m, dique seco:m, desembarcadero:m, dragón de mar:m",
  E: "estrella de mar:f, erizo:m, escollo:m, esturión:m, escuadra:f, espuma:f, estribor:m, embarcadero:m, escualo:m, espadarte:m, esponja:f, escotilla:f, esquife:m, escama:f, estuario:m, escafandra:f, eslora:f, ensenada:f, espigón:m, estrecho:m, estela:f",
  F: "faro:m, fragata:f, foca:f, flamenco:m, fiordo:m, flota:f, fondeadero:m, falucho:m, filibustero:m, fanal:m, flotador:m, foque:m, figura de proa:f, farallón:m, fogonero:m",
  G: "gaviota:f, galeón:m, gamba:f, grumete:m, garfio:m, gabarra:f, góndola:f, gorgonia:f, gaviero:m, garza:f, golfo:m, gusano marino:m, galera:f, gancho:m, gobio:m, guindola:f",
  H: "hélice:f, hipocampo:m, hamaca:f, holoturia:f, hidra:f, huracán:m, hipogloso:m, horizonte:m, hundimiento:m, hielo marino:m, hidrodeslizador:m",
  I: "isla:f, iceberg:m, islote:m, ictiosaurio:m, istmo:m, iguana marina:f, inmersión:f, isla desierta:f",
  J: "jibia:f, jurel:m, jábega:f, junco:m, jarcia:f, jaiba:f, jibión:m, jangada:f, jabeque:m",
  K: "kraken:m, kayak:m, kelp:m, krill:m",
  L: "langosta:f, lobo marino:m, lubina:f, lancha:f, leviatán:m, lenguado:m, lapa:f, lamprea:f, litoral:m, laguna:f, lastre:m, linterna:f, lombriz de mar:f, lampuga:f, lanchón:m, latitud:f",
  M: "medusa:f, mástil:m, merluza:f, marea:f, manatí:m, morena:f, mejillón:m, mero:m, mar:m, marinero:m, mascarón de proa:m, muelle:m, mantarraya:f, marlín:m, morsa:f, mastelero:m, maroma:f, monstruo marino:m, mojarra:f",
  N: "nautilo:m, náufrago:m, navío:m, nao:f, narval:m, nudo:m, nácar:m, niebla:f, nasa:f, nereida:f, nave:f, noray:m, nadador:m",
  O: "ostra:f, orca:f, océano:m, ola:f, oleaje:m, ostrero:m, octópodo:m, oreja de mar:f, orilla:f, obenque:m, ojo de buey:m",
  P: "pulpo:m, pez espada:m, pirata:m, pingüino:m, popa:f, proa:f, puerto:m, pargo:m, percebe:m, perca:f, pez globo:m, plancton:m, pesquero:m, polizón:m, patache:m, pleamar:f, pez payaso:m, pelícano:m, pez luna:m, peñasco:m, pasarela:f, pailebote:m, pez vela:m, palangre:m, piragua:f",
  Q: "quilla:f, quisquilla:f, quelonio:m, quimera:f, quechemarín:m, quitón:m",
  R: "remo:m, raya:f, rémora:f, rape:m, red:f, regata:f, rompeolas:m, rodaballo:m, roca:f, rumbo:m, remolcador:m, ría:f, rizón:m, rascacio:m, rompehielos:m, robalo:m, rada:f, ron:m",
  S: "sirena:f, sardina:f, salmón:m, sextante:m, sepia:f, submarino:m, salmonete:m, salina:f, soga:f, sargazo:m, sonda:f, serpiente marina:f, salvavidas:m, sábalo:m, sirenio:m, sonar:m, sargo:m",
  T: "tiburón:m, tortuga:f, timón:m, tridente:m, tesoro:m, tormenta:f, tripulante:m, trainera:f, tonina:f, tintorera:f, tsunami:m, tritón:m, trasatlántico:m, tentáculo:m, traje de buzo:m, tramontana:f, timonel:m, torpedero:m, trirreme:m",
  U: "urca:f, uva de mar:f, ulva:f, unicornio de mar:m, ultramar:m",
  V: "velero:m, vela:f, ventolina:f, viento de popa:m, vieira:f, vigía:m, vela mayor:f, vikingo:m, vapor:m, velamen:m, varadero:m, vaca marina:f, vorágine:f, vela latina:f",
  W: "windsurf:m, wahoo:m, wakeboard:m, windjammer:m",
  X: "xebec:m, xifias:m, xilófago:m, xifosuro:m",
  Y: "yate:m, yola:f, yodo:m, yubarta:f",
  Z: "zorro marino:m, zafarrancho:m, zodiac:f, zostera:f, zifio:m, zambullida:f, zooplancton:m, zoea:f"
};

/* Adjetivos de danza, teatro, circo, movimiento, glamour y espectáculo (forma masculina) */
const APELLIDOS_RAW = {
  A: "acrobático, aclamado, ágil, airoso, alado, alegre, aplaudido, apasionado, ardiente, arrebatador, artístico, asombroso, ataviado, atrevido, audaz, aterciopelado, aéreo, adornado, arlequinesco, aleteante",
  B: "bailarín, bailón, barroco, bohemio, brillante, bromista, bufonesco, bullanguero, bullicioso, burbujeante, burlesco, bamboleante, bordado, bizarro, bravo, bello, brincador",
  C: "caleidoscópico, cabaretero, cantarín, carnavalesco, chic, chispeante, circense, clownesco, cautivador, coqueto, coreográfico, colorido, cómico, conmovedor, contorsionista, chillón, cinematográfico",
  D: "danzante, danzarín, deslumbrante, despampanante, dramático, divertido, dorado, dúctil, disfrazado, deslizante, desenfadado, dinámico, decorado, distinguido, delirante, disparatado, derrochador",
  E: "elegante, equilibrista, efervescente, espectacular, escénico, estrafalario, extravagante, exuberante, elástico, enmascarado, emplumado, eléctrico, encantador, estelar, excéntrico, esplendoroso, eufórico, exótico, escurridizo, enjoyado",
  F: "fabuloso, fantástico, farandulero, fascinante, fastuoso, festivo, fiestero, flamenco, flexible, flotante, fogoso, frívolo, fulgurante, fotogénico, fanfarrón, fugaz, fino, folclórico",
  G: "galante, gallardo, garboso, genial, gesticulador, gesticulante, gimnástico, giratorio, glamuroso, gozoso, gracioso, grácil, grandilocuente, galopante, gimnasta, glorioso",
  H: "hechicero, hechizante, hermoso, hilarante, hipnótico, histriónico, hábil, habilidoso, hiperactivo, hollywoodense, hiperbólico, humorístico, heroico, hipnotizante",
  I: "ilusionista, imponente, impactante, impecable, improvisado, increíble, ingenioso, ingrávido, inquieto, intrépido, irresistible, irreverente, iridiscente, iluminado, ilustre, impetuoso, itinerante, inagotable",
  J: "jaranero, jazzístico, jocoso, jocundo, jovial, jubiloso, juerguista, juglaresco, juguetón, juvenil, jactancioso, jaleador",
  K: "kitsch, kinético, kaleidoscópico",
  L: "lánguido, laureado, lentejuelado, legendario, ligero, liviano, libre, lírico, llamativo, loco, lúdico, lujoso, luminoso, luciente, lustroso",
  M: "magistral, mágico, magnético, magnífico, majestuoso, malabarista, maquillado, maravilloso, mascarado, melódico, melodioso, mimoso, mímico, movedizo, multicolor, mundano, musical",
  N: "nacarado, nervioso, nítido, noble, noctámbulo, nocturno, nómada, notable, novedoso, novelero",
  O: "ondeante, ondulante, operístico, opulento, orquestal, original, orgulloso, osado, ostentoso, ovacionado, ocurrente, oscilante, olímpico",
  P: "palpitante, pantomímico, pasional, payasesco, picaresco, pícaro, pimpante, pintoresco, pizpireto, plateado, plumoso, poético, pomposo, precioso, prodigioso, pletórico, perfumado",
  Q: "quimérico, quijotesco, querido",
  R: "radiante, rebelde, refinado, refulgente, regio, resplandeciente, revoltoso, revoloteante, rítmico, rimbombante, risueño, rococó, rodante, rotundo, rumbero, rutilante, ruidoso, rebosante",
  S: "saltarín, saltimbanqui, salsero, sedoso, seductor, sensacional, sensual, serpentino, sinfónico, sincopado, sinuoso, sofisticado, solista, sonoro, sonriente, soberbio, sublime, suntuoso, sutil",
  T: "tambaleante, tanguero, taconeador, teatral, tentador, titilante, tornasolado, trágico, trapecista, travieso, tremendo, trepidante, triunfal, tropical, tintineante, transparente",
  U: "ufano, único, ultramoderno, uniformado, ululante, universal, utópico",
  V: "valiente, vanguardista, vanidoso, vaporoso, vertiginoso, versátil, vibrante, vigoroso, virtuoso, vistoso, vívido, vivaracho, vivaz, vodevilesco, volador, voluptuoso, veloz",
  W: "wagneriano, warholiano",
  X: "xilofónico, xenófilo",
  Y: "yeyé, yóguico, yámbico",
  Z: "zalamero, zancudo, zapateador, zarzuelero, zigzagueante, zumbón, zaragatero"
};
/*ENDDATA*/

/*GRAM*/
var INVARIABLES_OR = ["multicolor"];
function femenino(a) {
  if (INVARIABLES_OR.indexOf(a) >= 0) return a;
  if (/o$/.test(a)) return a.slice(0, -1) + "a";
  if (/ón$/.test(a)) return a.slice(0, -2) + "ona";
  if (/ín$/.test(a)) return a.slice(0, -2) + "ina";
  if (/or$/.test(a)) return a + "a";
  return a;
}
function neutro(a) {
  if (INVARIABLES_OR.indexOf(a) >= 0) return a;
  if (/án$/.test(a)) return a.slice(0, -2) + "ane";
  if (/ón$/.test(a)) return a.slice(0, -2) + "one";
  if (/ín$/.test(a)) return a.slice(0, -2) + "ine";
  if (/or$/.test(a)) return a + "e";
  if (/o$/.test(a)) return a.slice(0, -1) + "e";
  return a;
}
function adjetivo(a, g) { return g === "f" ? femenino(a) : g === "n" ? neutro(a) : a; }
function articulosNeutros(s) {
  return s.replace(/\bdel\b/g, "de le").replace(/\b(el|la)\b/g, "le").replace(/\b(los|las)\b/g, "les");
}
function cargoPara(t, g) {
  var m = t.match(/^(\S+)\|(\S+)(.*)$/);
  if (!m) return g === "n" ? articulosNeutros(t) : t;
  var resto = g === "n" ? articulosNeutros(m[3]) : m[3];
  return (g === "f" ? m[2] : g === "n" ? neutro(m[1]) : m[1]) + resto;
}
/*ENDGRAM*/
  var root = document.getElementById('crew'); if (!root) return;
  var T = JSON.parse(document.getElementById('crew-i18n').textContent);
  var LANG = document.documentElement.lang || 'es';
  var LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
  var MINUSCULAS = ["de", "del", "la", "el", "le", "los", "las", "les", "y", "a"];
  var NOMBRES = {}, APELLIDOS = {};
  LETRAS.forEach(function (l) {
    NOMBRES[l] = (NOMBRES_RAW[l] || "").split(",").map(function (x) { return x.trim(); }).filter(Boolean).map(function (x) {
      var i = x.lastIndexOf(":"); return { w: x.slice(0, i), g: x.slice(i + 1) };
    });
    APELLIDOS[l] = (APELLIDOS_RAW[l] || "").split(",").map(function (x) { return x.trim(); }).filter(Boolean);
  });
  var monthNames = [];
  for (var i = 0; i < 12; i++) {
    var n; try { n = new Intl.DateTimeFormat(LANG, { month: 'long' }).format(new Date(2026, i, 15)); } catch (e) { n = MESES[i].n; }
    monthNames.push(n.charAt(0).toUpperCase() + n.slice(1));
  }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function mayus(s) {
    return s.split(" ").map(function (w, i) {
      if (i > 0 && MINUSCULAS.indexOf(w) >= 0) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(" ");
  }
  var $ = function (id) { return document.getElementById(id); };
  var card = $("crew-card");
  var st = { mes: new Date().getMonth(), a: pick(LETRAS), b: pick(LETRAS), g: "m", r: null };
  var timer = null;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function elegir() {
    return { cargoIdx: Math.floor(Math.random() * cargos().length),
      nn: D ? pick(pool(D.nouns, D.adjFirst ? st.b : st.a)) : pick(NOMBRES[st.a]),
      aj: D ? pick(pool(D.adj, D.adjFirst ? st.a : st.b)) : pick(APELLIDOS[st.b]),
      mat: mesCorto(st.mes) + "-" + String(Math.floor(Math.random() * 10000)).padStart(4, "0") + "-" + st.a + st.b };
  }
  var D = window.CREW_DATA || null;
  var GI = { m: 0, f: 1, n: 2 };
  function forma(t) {
    var m = t.match(/^(\S+)\|(\S+)\|(\S+)(.*)$/);
    return m ? m[1 + (D.gender ? GI[st.g] : 0)] + m[4] : t;
  }
  function pool(o, l) {
    if (o[l] && o[l].length) return o[l];
    var all = []; Object.keys(o).forEach(function (k) { all = all.concat(o[k]); }); return all;
  }
  var mesCorto = function (i) { return MESES[i].n.slice(0, 3).toUpperCase(); };
  if (D) {
    var plain = monthNames.map(function (n) { return n.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase(); });
    var abbr = plain.map(function (n, i) {
      if (LANG === 'ja') return String(i + 1).padStart(2, "0") + "M";
      var a = n.slice(0, 3);
      return plain.filter(function (o) { return o.slice(0, 3) === a; }).length > 1 ? n.slice(0, 4) : a;
    });
    mesCorto = function (i) { return abbr[i]; };
  }
  function nombreCompleto(r) {
    if (D) {
      var i = r.nn.lastIndexOf(":"), n = i > 0 ? r.nn.slice(0, i) : r.nn, ng = i > 0 ? r.nn.slice(i + 1) : "", a = forma(r.aj);
      if (D.agree && ng && (D.invariant || []).indexOf(a) < 0) a = ((D.stems || {})[a] || a) + D.agree[ng];
      return D.adjFirst ? a + (D.joiner != null ? D.joiner : " ") + n : n + " " + a;
    }
    return mayus(r.nn.w) + " " + mayus(adjetivo(r.aj, st.g));
  }
  function cargoDe(t) { return D ? forma(t) : cargoPara(t, st.g); }
  function cargos() { return D ? D.months[st.mes] : MESES[st.mes].t; }
  function cargoActual(r) { return cargoDe(cargos()[r.cargoIdx]); }
  function render() {
    var r = st.r;
    $("crew-cargo").textContent = cargoActual(r);
    $("crew-nombre").textContent = nombreCompleto(r);
    $("crew-mat").textContent = r.mat;
    $("crew-meta").textContent = T.meta.replace('{m}', ['ca', 'es', 'fr', 'it', 'pt'].indexOf(LANG) < 0 ? monthNames[st.mes] : monthNames[st.mes].toLowerCase()).replace('{a}', st.a).replace('{b}', st.b);
  }
  function flicker() { var f = elegir(); $("crew-cargo").textContent = cargoDe(pick(cargos())); $("crew-nombre").textContent = nombreCompleto(f); }
  function anunciar() { $("crew-anuncio").textContent = nombreCompleto(st.r) + ", " + cargoActual(st.r) + "."; }
  function tirar() {
    var final = elegir(); $("crew-estado").textContent = "";
    if (reduce || document.documentElement.classList.contains('a11y-motion')) { st.r = final; render(); anunciar(); return; }
    var k = 0; clearInterval(timer); card.classList.add("rolling");
    timer = setInterval(function () {
      k++;
      if (k >= 9) { clearInterval(timer); card.classList.remove("rolling"); st.r = final; render(); anunciar(); }
      else flicker();
    }, 70);
  }
  function marcar(c, attr, v) { c.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute(attr) === String(v))); }); }
  var cm = $("crew-meses");
  monthNames.forEach(function (m, i) {
    var b = document.createElement("button"); b.type = "button"; b.className = "crew-month"; b.setAttribute("data-i", i); b.textContent = m;
    b.addEventListener("click", function () { st.mes = i; marcar(cm, "data-i", i); tirar(); }); cm.appendChild(b);
  });
  marcar(cm, "data-i", st.mes);
  [["crew-letras-nombre", "a"], ["crew-letras-apellido", "b"]].forEach(function (p) {
    var c = $(p[0]);
    LETRAS.forEach(function (l) {
      var b = document.createElement("button"); b.type = "button"; b.className = "crew-letter"; b.setAttribute("data-l", l);
      b.setAttribute("aria-label", T.letter + " " + l); b.textContent = l;
      b.addEventListener("click", function () { st[p[1]] = l; marcar(c, "data-l", l); tirar(); }); c.appendChild(b);
    });
    marcar(c, "data-l", st[p[1]]);
  });
  var cg = $("crew-genero"); marcar(cg, "data-g", st.g);
  cg.querySelectorAll("button").forEach(function (b) {
    b.addEventListener("click", function () { st.g = b.getAttribute("data-g"); marcar(cg, "data-g", st.g); if (st.r) { render(); anunciar(); } });
  });
  $("crew-otra").addEventListener("click", tirar);
  $("crew-sorpresa").addEventListener("click", function () {
    st.mes = Math.floor(Math.random() * 12); st.a = pick(LETRAS); st.b = pick(LETRAS);
    marcar(cm, "data-i", st.mes); marcar($("crew-letras-nombre"), "data-l", st.a); marcar($("crew-letras-apellido"), "data-l", st.b); tirar();
  });
  $("crew-copiar").addEventListener("click", function () {
    var txt = nombreCompleto(st.r) + ", " + cargoActual(st.r) + " · VENDAVAL";
    var ok = function () { $("crew-estado").textContent = T.copied + " " + txt; };
    var sel = function () { var r = document.createRange(); r.selectNodeContents($("crew-nombre")); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); $("crew-estado").textContent = T.selected; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(ok, sel); else sel();
  });
  st.r = elegir(); render(); anunciar();
})();
