package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	_ "modernc.org/sqlite"
)

// bit of a hack but sqlite with modernc means no CGO dep
var db *sql.DB

type Content struct {
	ID        int      `json:"id"`
	Title     string   `json:"title"`
	Body      string   `json:"body"`
	Category  string   `json:"category"`
	Language  string   `json:"language"`
	Tags      []string `json:"tags"`
	Summary   string   `json:"summary"`
	CreatedAt string   `json:"created_at"`
}

type Question struct {
	ID        int    `json:"id"`
	Question  string `json:"question"`
	Answer    string `json:"answer"`
	Language  string `json:"language"`
	Category  string `json:"category"`
	CreatedAt string `json:"created_at"`
}

type EmergencyAlert struct {
	ID        int      `json:"id"`
	Title     string   `json:"title"`
	Body      string   `json:"body"`
	Severity  string   `json:"severity"`
	Regions   []string `json:"regions"`
	CreatedAt string   `json:"created_at"`
	ExpiresAt string   `json:"expires_at"`
}

type Language struct {
	Code string `json:"code"`
	Name string `json:"name"`
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	var err error
	db, err = sql.Open("sqlite", "./bridge.db")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	initDB()

	// Single top-level handler routes everything
	fs := http.FileServer(http.Dir("../frontend/dist"))
	mux := http.NewServeMux()
	mux.Handle("/", fs)

	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		path := r.URL.Path
		switch {
		case r.Method == "GET" && path == "/api/health":
			json.NewEncoder(w).Encode(map[string]string{"status": "ok", "service": "bridge"})
		case r.Method == "GET" && path == "/api/languages":
			handleGetLanguages(w, r)
		case r.Method == "GET" && path == "/api/content":
			handleGetContent(w, r)
		case r.Method == "GET" && strings.HasPrefix(path, "/api/content/search"):
			handleSearchContent(w, r)
		case r.Method == "GET" && strings.HasPrefix(path, "/api/content/category/"):
			r.SetPathValue("category", strings.TrimPrefix(path, "/api/content/category/"))
			handleGetContentByCategory(w, r)
		case r.Method == "GET" && strings.HasPrefix(path, "/api/content/"):
			r.SetPathValue("id", strings.TrimPrefix(path, "/api/content/"))
			handleGetContentByID(w, r)
		case r.Method == "POST" && path == "/api/ai/ask":
			handleAIAsk(w, r)
		case r.Method == "GET" && path == "/api/questions":
			handleGetQuestions(w, r)
		case r.Method == "POST" && path == "/api/questions":
			handlePostQuestion(w, r)
		case r.Method == "POST" && strings.HasPrefix(path, "/api/questions/") && strings.HasSuffix(path, "/answer"):
			id := strings.TrimPrefix(path, "/api/questions/")
			id = strings.TrimSuffix(id, "/answer")
			id = strings.TrimSuffix(id, "/")
			r.SetPathValue("id", id)
			handlePostAnswer(w, r)
		case r.Method == "GET" && path == "/api/alerts":
			handleGetAlerts(w, r)
		case r.Method == "GET" && path == "/api/alerts/active":
			handleGetActiveAlerts(w, r)
		default:
			mux.ServeHTTP(w, r)
		}
	})

	addr := fmt.Sprintf(":%s", port)
	log.Printf("Bridge backend starting on %s", addr)
	log.Fatal(http.ListenAndServe(addr, handler))
}

func initDB() {
	schema := `
	CREATE TABLE IF NOT EXISTS content (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		title TEXT NOT NULL,
		body TEXT NOT NULL,
		category TEXT NOT NULL,
		language TEXT NOT NULL DEFAULT 'en',
		tags TEXT DEFAULT '[]',
		summary TEXT DEFAULT '',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);

	CREATE TABLE IF NOT EXISTS questions (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		question TEXT NOT NULL,
		answer TEXT DEFAULT '',
		language TEXT DEFAULT 'en',
		category TEXT DEFAULT 'general',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);

	CREATE TABLE IF NOT EXISTS emergency_alerts (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		title TEXT NOT NULL,
		body TEXT NOT NULL,
		severity TEXT DEFAULT 'info',
		regions TEXT DEFAULT '[]',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		expires_at DATETIME
	);

	CREATE TABLE IF NOT EXISTS languages (
		code TEXT PRIMARY KEY,
		name TEXT NOT NULL
	);

	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		role TEXT DEFAULT 'user',
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);
	`
	if _, err := db.Exec(schema); err != nil {
		log.Fatal(err)
	}

	seedData()
}

func seedData() {
	// Seed languages
	languages := []struct{ code, name string }{
		{"en", "English"},
		{"sw", "Kiswahili"},
		{"fr", "Français"},
		{"es", "Español"},
		{"ar", "العربية"},
		{"zu", "isiZulu"},
		{"xh", "isiXhosa"},
		{"af", "Afrikaans"},
		{"ha", "Hausa"},
		{"yo", "Yoruba"},
		{"ig", "Igbo"},
		{"am", "Amharic"},
	}

	for _, l := range languages {
		db.Exec("INSERT OR IGNORE INTO languages (code, name) VALUES (?, ?)", l.code, l.name)
	}

	// Seed content if empty
	var count int
	db.QueryRow("SELECT COUNT(*) FROM content").Scan(&count)
	if count > 0 {
		return
	}

	content := []struct {
		title, body, category, language, summary string
		tags                                     []string
	}{
		{
			title:    "Clean Water Basics",
			body:     "Access to clean water is essential for health. Boil water for at least 1 minute before drinking if unsure of its safety. Use chlorine tablets or water filters when available. Store water in clean, covered containers. Signs of waterborne illness include diarrhea, vomiting, and stomach cramps. Seek medical help if symptoms persist.",
			category: "health",
			language: "en",
			summary:  "How to ensure safe drinking water without modern infrastructure",
			tags:     []string{"water", "health", "hygiene", "basics"},
		},
		{
			title:    "Msingi wa Maji Safi",
			body:     "Kupata maji safi ni muhimu kwa afya. Chemsha maji kwa dakika moja kabla ya kunywa ikiwa huna uhakika wa usalama wake. Tumia vidonge vya kusafisha maji au vichujio vya maji vinapopatikana. Hifadhi maji kwenye vyombo safi vilivyofunikwa. Dalili za magonjwa ya maji ni pamoja na kuhara, kutapika, na maumivu ya tumbo. Tafuta msaada wa matibabu ikiwa dalili zinaendelea.",
			category: "health",
			language: "sw",
			summary:  "Jinsi ya kuhakikisha maji safi ya kunywa bila miundombinu ya kisasa",
			tags:     []string{"maji", "afya", "usafi"},
		},
		{
			title:    "Premiers Soins de Base",
			body:     "En cas d'urgence médicale, restez calme et évaluez la situation. Vérifiez si la personne est consciente et respire. Pour les saignements, appliquez une pression directe sur la plaie avec un chiffon propre. Pour les brûlures, refroidissez sous l'eau courante pendant au moins 10 minutes. Appelez les services d'urgence si nécessaire. Gardez une trousse de premiers soins à portée de main avec des bandages, des antiseptiques et des gants.",
			category: "health",
			language: "fr",
			summary:  "Gestes de premiers secours pour les zones sans accès immédiat aux soins",
			tags:     []string{"premiers soins", "santé", "urgence"},
		},
		{
			title:    "Emergency Preparedness",
			body:     "In case of natural disasters: 1) Know your evacuation routes. 2) Keep an emergency kit with water, food, first aid, flashlight, and batteries. 3) Have a family communication plan. 4) Stay informed via radio or SMS alerts. 5) Know where your local shelter is. 6) Charge devices when warnings are issued. 7) Help neighbors who may need assistance.",
			category: "emergency",
			language: "en",
			summary:  "Essential steps to prepare for natural disasters and emergencies",
			tags:     []string{"disaster", "preparedness", "safety", "emergency"},
		},
		{
			title:    "Maandalizi ya Dharura",
			body:     "Katika tukio la maafa ya asili: 1) Jua njia za uokoaji. 2) Weka vifaa vya dharura: maji, chakula, mwanga, betri. 3) Kuwa na mpango wa mawasiliano ya familia. 4) Pata taarifa kupitia redio au SMS. 5) Jua mahali pa makazi ya dharura. 6) Chaja vifaa vya mawasiliano wakati tahadhari zinatolewa. 7) Saidia majirani wanaohitaji msaada.",
			category: "emergency",
			language: "sw",
			summary:  "Hatua muhimu za kujiandaa kwa maafa ya asili na dharura",
			tags:     []string{"maafa", "maandalizi", "usalama"},
		},
		{
			title:    "Your Legal Rights: Know the Basics",
			body:     "Everyone has fundamental legal rights regardless of their status. You have the right to: 1) Be treated with dignity and respect. 2) Access education for your children. 3) Receive emergency medical care. 4) Fair treatment under the law. 5) Freedom from discrimination. 6) Access to legal representation. If you believe your rights have been violated, document everything, seek help from legal aid organizations, and contact human rights commissions.",
			category: "legal",
			language: "en",
			summary:  "Basic legal rights everyone should know",
			tags:     []string{"rights", "legal", "justice", "basics"},
		},
		{
			title:    "Haki Zako za Kisheria",
			body:     "Kila mtu ana haki za kimsingi za kisheria bila kujali hadhi yake. Una haki ya: 1) Kutendewa kwa heshima na utu. 2) Kupata elimu kwa watoto wako. 3) Kupata matibabu ya dharura. 4) Kutendewa kwa haki chini ya sheria. 5) Uhuru kutoka kwa ubaguzi. 6) Kupata uwakilishi wa kisheria. Ikiwa unaamini haki zako zimekiukwa, andika kila kitu, tafuta msaada kutoka kwa mashirika ya usaidizi wa kisheria, na wasiliana na tume za haki za binadamu.",
			category: "legal",
			language: "sw",
			summary:  "Haki za kimsingi za kisheria kila mtu anapaswa kujua",
			tags:     []string{"haki", "sheria", "haki za binadamu"},
		},
		{
			title:    "Basic Math Skills",
			body:     "Mathematics is essential for daily life. Addition: combining numbers. Subtraction: taking away. Multiplication: repeated addition. Division: splitting into equal parts. Practice with real examples: calculating change, measuring ingredients, splitting bills. Use your phone's calculator or ask for help at local community centers.",
			category: "education",
			language: "en",
			summary:  "Fundamental math skills for everyday life",
			tags:     []string{"math", "education", "basics", "numeracy"},
		},
		{
			title:    "Stadi za Msingi za Hisabati",
			body:     "Hisabati ni muhimu kwa maisha ya kila siku. Kujumlisha: kuunganisha namba. Kutoa: kuondoa. Kuzidisha: kurudia kujumlisha. Kugawanya: kugawanya kwa sehemu sawa. Fanya mazoezi na mifano halisi: kuhesabu changio, kupima viungo, kugawanya bili. Tumia kikokotoo cha simu yako au uliza msaada katika vituo vya jamii.",
			category: "education",
			language: "sw",
			summary:  "Stadi za msingi za hisabati kwa maisha ya kila siku",
			tags:     []string{"hisabati", "elimu", "msingi"},
		},
		{
			title:    "Derechos Humanos Fundamentales",
			body:     "Toda persona tiene derechos humanos fundamentales. Estos incluyen: derecho a la vida, libertad y seguridad; libertad de expresión; derecho a la educación; derecho a la salud; derecho al trabajo; derecho a un juicio justo; libertad de discriminación. Si tus derechos son violados, documenta todo, busca ayuda de organizaciones de derechos humanos, y contacta a la comisión de derechos humanos de tu país.",
			category: "legal",
			language: "es",
			summary:  "Derechos humanos básicos que todos deben conocer",
			tags:     []string{"derechos", "humanos", "justicia"},
		},
		{
			title:    "Nutrition for Children",
			body:     "Proper nutrition is critical for children's development. Key nutrients: protein (beans, eggs, meat), carbohydrates (rice, maize, potatoes), vitamins (fruits, vegetables), and minerals. Children need 3 meals a day with healthy snacks. Breastfeeding is recommended for the first 6 months. Clean water is essential. Signs of malnutrition: weight loss, tiredness, frequent illness. Seek help from local health clinics.",
			category: "health",
			language: "en",
			summary:  "Essential nutrition guidelines for child development",
			tags:     []string{"nutrition", "children", "health", "development"},
		},
		{
			title:    "Financial Literacy: Saving Basics",
			body:     "Saving money helps you prepare for the future. Start small - even a little each week adds up. Keep savings separate from daily spending money. Use a savings group, bank account, or mobile money. Track your income and expenses. Set a goal: school fees, emergency fund, or a small business. Avoid high-interest loans. Ask about community savings programs.",
			category: "education",
			language: "en",
			summary:  "Basic financial literacy and saving strategies",
			tags:     []string{"finance", "savings", "education", "money"},
		},
		{
			title:    "Elimu ya Fedha: Msingi wa Kuweka Akiba",
			body:     "Kuweka akiba kunakusaidia kujiandaa kwa siku zijazo. Anza kidogo - hata kiasi kidogo kila wiki kinajumlishka. Weka akiba tofauti na pesa za matumizi ya kila siku. Tumia kikundi cha kuweka akiba, akaunti ya benki, au pesa za simu. Fuatilia mapato na matumizi yako. Weka lengo: ada za shule, dharura, au biashara ndogo. Epuka mikopo ya riba kubwa.",
			category: "education",
			language: "sw",
			summary:  "Mbinu za msingi za kusimamia fedha na kuweka akiba",
			tags:     []string{"fedha", "akiba", "elimu", "pesa"},
		},
		{
			title:    "Emergency First Aid",
			body:     "In a medical emergency: 1) Stay calm and assess the situation. 2) Check if the person is conscious and breathing. 3) For bleeding, apply direct pressure with a clean cloth. 4) For burns, cool under running water for 10 minutes. 5) For fractures, immobilize the area and seek help. 6) Call emergency services if available. 7) Do not move someone with a suspected neck or spine injury.",
			category: "health",
			language: "en",
			summary:  "Life-saving first aid procedures for emergencies",
			tags:     []string{"first aid", "emergency", "health", "safety"},
		},
		{
			title:    "Digital Rights & Safety",
			body:     "You have rights online too. Protect your privacy: use strong passwords, don't share personal information with strangers, be careful what you post. Know that surveillance and data collection are common. Use encrypted messaging apps when possible. Report online harassment. Digital literacy is a skill - learn to spot misinformation and scams.",
			category: "legal",
			language: "en",
			summary:  "Understanding your rights and staying safe online",
			tags:     []string{"digital", "rights", "privacy", "safety"},
		},
		{
			title:    "Haki za Dijitali na Usalama",
			body:     "Una haki mtandaoni pia. Linda faragha yako: tumia nywila kali, usishiriki taarifa za kibinafsi na wageni, kuwa makini kile unachochapisha. Jua kwamba ufuatiliaji na ukusanyaji wa data ni jambo la kawaida. Tumia programu za ujumbe zilizosimbwa inapowezekana. Ripoti unyanyasaji mtandaoni. Ujuzi wa dijitali ni stadi - jifunze kutambua habari za uongo na ulaghai.",
			category: "legal",
			language: "sw",
			summary:  "Kuelewa haki zako na kukaa salama mtandaoni",
			tags:     []string{"dijitali", "haki", "faragha", "usalama"},
		},
		{
			title:    "Derechos Digitales y Seguridad",
			body:     "También tienes derechos en línea. Protege tu privacidad: usa contraseñas seguras, no compartas información personal con extraños, ten cuidado con lo que publicas. El monitoreo y la recopilación de datos son comunes. Usa aplicaciones de mensajería cifrada cuando sea posible. Denuncia el acoso en línea. La alfabetización digital es una habilidad: aprende a detectar desinformación y estafas.",
			category: "legal",
			language: "es",
			summary:  "Comprender tus derechos y mantenerte seguro en línea",
			tags:     []string{"digital", "derechos", "privacidad", "seguridad"},
		},
		{
			title:    "Pregnancy & Newborn Care",
			body:     "Pregnancy care: attend prenatal checkups, eat nutritious food, take iron and folic acid supplements, rest adequately. Danger signs: severe bleeding, severe headaches, blurred vision, high fever, difficulty breathing - seek help immediately. Newborn care: breastfeed exclusively for 6 months, keep baby warm, clean umbilical cord with dry cloth, vaccinate on schedule. Register the birth.",
			category: "health",
			language: "en",
			summary:  "Essential care guidelines for pregnancy and newborns",
			tags:     []string{"pregnancy", "newborn", "maternal", "health"},
		},
		{
			title:    "Huduma ya Mimba na Mtoto Mchanga",
			body:     "Huduma ya mimba: hudhuria vipimo vya ujauzito, kula vyakula vyenye virutubisho, chukua virutubisho vya chuma na asidi ya folic, pumzika vya kutosha. Dalili za hatari: kutokwa na damu nyingi, maumivu makali ya kichwa, macho yenye ukungu, homa kali, shida ya kupumua - tafuta msaada mara moja. Huduma ya mtoto mchanga: nyonyesha kwa miezi 6, mweke mtoto joto, safisha kitovu kwa kitambaa kavu, pata chanjo kwa ratiba. Sasisha kuzaliwa.",
			category: "health",
			language: "sw",
			summary:  "Mwongozo muhimu wa huduma ya mimba na watoto wachanga",
			tags:     []string{"mimba", "mtoto mchanga", "afya ya mama"},
		},
		{
			title:    "Derechos de la Mujer",
			body:     "Las mujeres tienen derecho a: 1) Igualdad de trato ante la ley. 2) Acceso a educación y empleo. 3) Atención médica, incluida la salud reproductiva. 4) Vivir libres de violencia y discriminación. 5) Participar en la vida política y pública. 6) Propiedad y herencia. 7) Tomar decisiones sobre su propio cuerpo. Si enfrentas discriminación o violencia, busca ayuda de organizaciones de derechos de la mujer y líneas de ayuda.",
			category: "legal",
			language: "es",
			summary:  "Derechos fundamentales de la mujer que toda persona debe conocer",
			tags:     []string{"mujer", "derechos", "igualdad", "justicia"},
		},
		{
			title:    "Haki za Wanawake",
			body:     "Wanawake wana haki ya: 1) Kutendewa kwa usawa mbele ya sheria. 2) Kupata elimu na ajira. 3) Kupata huduma za afya, ikijumuisha afya ya uzazi. 4) Kuishi bila vurugu na ubaguzi. 5) Kushiriki katika siasa na maisha ya umma. 6) Kumiliki mali na urithi. 7) Kufanya maamuzi kuhusu mwili wao wenyewe. Ikiwa unakabiliwa na ubaguzi au vurugu, tafuta msaada kutoka kwa mashirika ya haki za wanawake.",
			category: "legal",
			language: "sw",
			summary:  "Haki za msingi za wanawake kila mtu anapaswa kujua",
			tags:     []string{"wanawake", "haki", "usawa", "haki za binadamu"},
		},
		{
			title:    "Soins Prénatals et Postnatals",
			body:     "Soins de grossesse: assistez aux consultations prénatales, mangez des aliments nutritifs, prenez des suppléments de fer et d'acide folique, reposez-vous suffisamment. Signes de danger: saignements abondants, maux de tête sévères, vision trouble, forte fièvre, difficulté à respirer - consultez immédiatement. Soins du nouveau-né: allaitement exclusif pendant 6 mois, gardez le bébé au chaud, nettoyez le cordon ombilical avec un chiffon sec, vaccins selon le calendrier.",
			category: "health",
			language: "fr",
			summary:  "Soins essentiels pour la grossesse et les nouveau-nés",
			tags:     []string{"grossesse", "nouveau-né", "santé maternelle"},
		},
		{
			title:    "Hausa: Kula da Lafiya",
			body:     "Kula da lafiyar jiki yana da muhimmanci. Sha ruwa mai tsafta, ci abinci mai gina jiki, yi motsa jiki akai-akai, kuma yi barci mai kyau. Wanke hannuwanka da sabulu kafin ci. Yi alluran rigakafi a kan lokaci. Idan ba ka ji daɗi, je asibiti ko kuma nemi taimako daga ma'aikatan lafiya. Kula da lafiyar hankali shima yana da muhimmanci - yi magana da wanda ka amince da shi idan kana jin damuwa.",
			category: "health",
			language: "ha",
			summary:  "Muhimman hanyoyin kula da lafiyar jiki da hankali",
			tags:     []string{"lafiya", "kula da jiki", "tsafta"},
		},
		{
			title:    "Emergency Contacts & Resources",
			body:     "Keep these numbers handy: Police emergency, Ambulance, Fire department, Local hospital, Poison control, Women's helpline, Child protection services. Save them in your phone and write them down somewhere accessible. In an emergency, stay calm, state your location clearly, and describe the situation. If you don't have phone credit, many emergency numbers work even without credit.",
			category: "emergency",
			language: "en",
			summary:  "Essential emergency contact numbers and what to do",
			tags:     []string{"emergency", "contacts", "safety", "helplines"},
		},
		{
			title:    "Nambari za Dharura na Rasilimali",
			body:     "Weka nambari hizi karibu: Polisi wa dharura, Ambulensi, Zima moto, Hospitali ya karibu, Kidhibiti cha sumu, Mstari wa msaada wa wanawake, Huduma za ulinzi wa watoto. Zihifadhi kwenye simu yako na uziandike mahali panapoweza kufikiwa. Katika dharura, tulia, eleza mahali ulipo kwa uwazi, na eleza hali hiyo. Ikiwa huna kiasi cha simu, nambari nyingi za dharura hufanya kazi hata bila kiasi.",
			category: "emergency",
			language: "sw",
			summary:  "Nambari muhimu za dharura na nini cha kufanya",
			tags:     []string{"dharura", "mawasiliano", "usalama", "msaada"},
		},
		{
			title:    "Climate Resilience: Protecting Your Farm",
			body:     "Climate change affects everyone. Protect your farm: plant drought-resistant crops, use water conservation techniques (mulching, drip irrigation), diversify your crops, plant trees for shade and windbreaks, store water during rainy seasons. Join local farmer cooperatives to share resources and knowledge. Monitor weather forecasts when available. Consider drought-resistant livestock breeds.",
			category: "education",
			language: "en",
			summary:  "Practical strategies for farming in a changing climate",
			tags:     []string{"climate", "farming", "resilience", "agriculture"},
		},
		{
			title:    "Ustahimilivu wa Hali ya Hewa: Kulinda Shamba Lako",
			body:     "Mabadiliko ya hali ya hewa yanaathiri kila mtu. Linda shamba lako: panda mazao yanayostahimili ukame, tumia mbinu za kuhifadhi maji (matandazo, umwagiliaji kwa njia ya matone), panda mazao mbalimbali, panda miti kwa kivuli na uzuiaji wa upepo, hifadhi maji wakati wa mvua. Jiunge na vyama vya wakulima vya ushirika ili kushiriki rasilimali na maarifa. Fuatilia utabiri wa hali ya hewa.",
			category: "education",
			language: "sw",
			summary:  "Mbinu za vitendo za kilimo katika mabadiliko ya hali ya hewa",
			tags:     []string{"hali ya hewa", "kilimo", "ustahimilivu"},
		},
		{
			title:    "Mental Health: You Are Not Alone",
			body:     "Mental health is as important as physical health. Signs you may need support: persistent sadness, loss of interest in activities, changes in sleep or appetite, difficulty concentrating, thoughts of self-harm. Talk to someone you trust. Reach out to community health workers. Practice self-care: rest, eat well, connect with others. Many communities have free counseling services. You are not alone.",
			category: "health",
			language: "en",
			summary:  "Recognizing mental health challenges and finding support",
			tags:     []string{"mental health", "wellness", "support", "self-care"},
		},
		{
			title:    "Afya ya Akili: Wewe Si Pekee Yako",
			body:     "Afya ya akili ni muhimu kama afya ya mwili. Dalili za kuhitaji msaada: huzuni inayoendelea, kupoteza hamu ya shughuli, mabadiliko ya usingizi au hamu ya kula, ugumu wa kuzingatia, mawazo ya kujidhuru. Ongea na mtu unayemwamini. Wasiliana na wafanyakazi wa afya ya jamii. Jitunze: pumzika, kula vizuri, wasiliana na wengine. Jamii nyingi zina huduma za ushauri nasaha bila malipo. Wewe si pekee yako.",
			category: "health",
			language: "sw",
			summary:  "Kutambua changamoto za afya ya akili na kupata msaada",
			tags:     []string{"afya ya akili", "ustawi", "msaada", "kujitunza"},
		},
		{
			title:    "Starting a Small Business",
			body:     "Starting a small business can change your life. Steps: 1) Identify a problem in your community you can solve. 2) Start small - test your idea with minimal investment. 3) Track all income and expenses. 4) Save profits to grow. 5) Learn from customers. 6) Join local business groups for support. 7) Use mobile money for transactions. Many successful businesses started with very little capital.",
			category: "education",
			language: "en",
			summary:  "Practical steps to start and grow a small business",
			tags:     []string{"business", "entrepreneurship", "finance", "skills"},
		},
		{
			title:    "Kuanzisha Biashara Ndogo",
			body:     "Kuanzisha biashara ndogo kunaweza kubadilisha maisha yako. Hatua: 1) Tambua tatizo katika jamii yako unaloweza kutatua. 2) Anza kidogo - jaribu wazo lako kwa uwekezaji mdogo. 3) Fuatilia mapato na matumizi yote. 4) Weka akiba ya faida ili kukua. 5) Jifunze kutoka kwa wateja. 6) Jiunge na vikundi vya biashara vya mitaa kwa msaada. 7) Tumia pesa za simu kwa shughuli. Biashara nyingi zilizofanikiwa zilianza na mtaji mdogo sana.",
			category: "education",
			language: "sw",
			summary:  "Hatua za vitendo za kuanzisha na kukuza biashara ndogo",
			tags:     []string{"biashara", "ujasiriamali", "fedha", "stadi"},
		},
		{
			title:    "Préparation aux Cyclones",
			body:     "Dans les zones sujettes aux cyclones: 1) Connaissez vos routes d'évacuation. 2) Renforcez votre maison si possible. 3) Préparez un kit d'urgence: eau, nourriture, lampe torche, radio, médicaments. 4) Écoutez les alertes météo. 5) Évacuez tôt si ordonné. 6) Protégez les documents importants dans un sac étanche. 7) Après le cyclone, méfiez-vous des lignes électriques tombées et des eaux de crue.",
			category: "emergency",
			language: "fr",
			summary:  "Préparation essentielle pour les cyclones et tempêtes",
			tags:     []string{"cyclone", "préparation", "sécurité", "urgence"},
		},
		{
			title:    "Haki za Watoto",
			body:     "Kila mtoto ana haki za msingi: 1) Haki ya kuishi na kukua. 2) Haki ya kupata elimu. 3) Haki ya kupata huduma za afya. 4) Haki ya kulindwa dhidi ya unyanyasaji na ukatili. 5) Haki ya kuwa na familia na kutengenezewa. 6) Haki ya kucheza na kupumzika. 7) Haki ya kutoa maoni yake. Ikiwa haki za mtoto zinakiukwa, ripoti kwa mamlaka za ulinzi wa watoto au mashirika yasiyo ya kiserikali.",
			category: "legal",
			language: "sw",
			summary:  "Haki za msingi za watoto kulingana na sheria za kimataifa",
			tags:     []string{"watoto", "haki", "ulinzi", "elimu"},
		},
		{
			title:    "Children's Rights",
			body:     "Every child has fundamental rights: 1) Right to life and development. 2) Right to education. 3) Right to healthcare. 4) Right to protection from abuse and exploitation. 5) Right to family and alternative care. 6) Right to play and rest. 7) Right to express their views. If a child's rights are violated, report to child protection authorities or NGOs. Every child deserves to grow up safe, healthy, and educated.",
			category: "legal",
			language: "en",
			summary:  "Fundamental children's rights under international law",
			tags:     []string{"children", "rights", "protection", "education"},
		},
		{
			title:    "Derechos del Niño",
			body:     "Todo niño tiene derechos fundamentales: 1) Derecho a la vida y al desarrollo. 2) Derecho a la educación. 3) Derecho a la atención médica. 4) Derecho a la protección contra el abuso y la explotación. 5) Derecho a la familia y al cuidado alternativo. 6) Derecho al juego y al descanso. 7) Derecho a expresar sus opiniones. Si se violan los derechos de un niño, repórtelo a las autoridades de protección infantil.",
			category: "legal",
			language: "es",
			summary:  "Derechos fundamentales de los niños según el derecho internacional",
			tags:     []string{"niños", "derechos", "protección", "educación"},
		},
		{
			title:    "Hausa: Hakkokin Yara",
			body:     "Kowane yaro yana da hakkoki na asali: 1) Hakkin rayuwa da ci gaba. 2) Hakkin ilimi. 3) Hakkin kula da lafiya. 4) Hakkin kariya daga cin zarafi. 5) Hakkin iyali da kulawa. 6) Hakkin wasa da hutu. 7) Hakkin bayyana ra'ayinsa. Idan an keta hakkokin yaro, kai rahoto ga hukumomin kare yara. Kowane yaro ya cancanci girma lafiya, aminci, da ilimi.",
			category: "legal",
			language: "ha",
			summary:  "Muhimman hakkokin yara a karkashin dokokin kasa da kasa",
			tags:     []string{"yara", "hakkoki", "kariya", "ilimi"},
		},
		{
			title:    "Flood Safety",
			body:     "During floods: 1) Move to higher ground immediately. 2) Do not walk or drive through flood water - 6 inches can knock you over. 3) Avoid electrical equipment in water. 4) Turn off gas and electricity if safe. 5) Listen to emergency services. 6) After flooding, avoid contact with flood water (may be contaminated). 7) Check for structural damage before entering buildings. 8) Document damage for aid applications.",
			category: "emergency",
			language: "en",
			summary:  "Critical safety guidelines for flood situations",
			tags:     []string{"flood", "safety", "emergency", "disaster"},
		},
		{
			title:    "Usalama wa Mafuriko",
			body:     "Wakati wa mafuriko: 1) Nenda sehemu za juu mara moja. 2) Usitembee au kuendesha gari kwenye maji ya mafuriko - inchi 6 zinaweza kukuangusha. 3) Epuka vifaa vya umeme vilivyo ndani ya maji. 4) Zima gesi na umeme ikiwa ni salama. 5) Sikiliza maagizo ya huduma za dharura. 6) Baada ya mafuriko, epuka kugusa maji ya mafuriko (yanaweza kuwa yamechafuliwa). 7) Angalia uharibifu wa muundo kabla ya kuingia majengo.",
			category: "emergency",
			language: "sw",
			summary:  "Mwongozo muhimu wa usalama wakati wa mafuriko",
			tags:     []string{"mafuriko", "usalama", "dharura", "maafa"},
		},
		{
			title:    "Hausa: Tsaron Ambaliyar Ruwa",
			body:     "Lokacin ambaliyar ruwa: 1) Tashi zuwa wuri mai tsayi nan take. 2) Kada ku yi tafiya a cikin ruwan ambaliya - inci 6 na iya sa ka fadi. 3) Nisantar kayan lantarki a cikin ruwa. 4) Kashe gas da wutar lantarki idan lafiya. 5) Saurari umarnin jami'an gaggawa. 6) Bayan ambaliya, nisantar ruwan ambaliya (yana iya zama gurbatacce). 7) Duba lalacewar gini kafin shiga gine-gine.",
			category: "emergency",
			language: "ha",
			summary:  "Muhimman jagororin tsaro yayin ambaliyar ruwa",
			tags:     []string{"ambaliya", "tsaro", "gaggawa", "bala'i"},
		},
		{
			title:    "Hausa: Kula da Jiki da Hankali",
			body:     "Kula da lafiyar jiki da hankali yana da muhimmanci. Sha ruwa mai tsafta, ci abinci mai gina jiki, yi motsa jiki, kuma yi barci mai kyau. Wanke hannuwanka da sabulu. Yi alluran rigakafi. Idan ba ka ji daɗi, je asibiti. Kula da lafiyar hankali shima yana da muhimmanci - yi magana da wanda ka amince da shi idan kana jin damuwa. Kada ka yi shiru - taimako yana nan.",
			category: "health",
			language: "ha",
			summary:  "Muhimman hanyoyin kula da lafiyar jiki da hankali",
			tags:     []string{"lafiya", "kula da jiki", "tsafta", "hankali"},
		},
		{
			title:    "Hausa: Hakkokin Dan Adam",
			body:     "Kowane mutum yana da hakkoki na asali: 1) Hakkin rayuwa da 'yanci. 2) Hakkin ilimi. 3) Hakkin kula da lafiya. 4) Hakkin aiki. 5) Hakkin shari'a ta gaskiya. 6) 'Yanci daga nuna bambanci. 7) Hakkin magana. Idan an keta hakkokinka, rubuta komai, nemi taimako daga kungiyoyin kare hakkin dan adam, kuma tuntuɓi kwamitocin hakkin dan adam.",
			category: "legal",
			language: "ha",
			summary:  "Muhimman hakkokin dan adam da kowa ya kamata ya sani",
			tags:     []string{"hakki", "dan adam", "shari'a", "adalci"},
		},
		{
			title:    "Hausa: Shirye-shiryen Gaggawa",
			body:     "A yayin bala'i: 1) San hanyoyin ƙaura. 2) Shirya kayan gaggawa: ruwa, abinci, fitila, rediyo, magunguna. 3) Sami tsarin sadarwa na iyali. 4) Saurari faɗakarwa ta rediyo ko SMS. 5) San inda matsugunin gaggawa yake. 6) Caja na'urori lokacin da aka ba da faɗakarwa. 7) Taimaki maƙwabta waɗanda ke buƙatar taimako. Shirye-shirye na iya ceton rayuka.",
			category: "emergency",
			language: "ha",
			summary:  "Muhimman matakan shirye-shiryen bala'i",
			tags:     []string{"bala'i", "shiri", "tsaro", "gaggawa"},
		},
		{
			title:    "Hausa: Kula da Jiki da Hankali",
			body:     "Kula da lafiyar jiki da hankali yana da muhimmanci. Sha ruwa mai tsafta, ci abinci mai gina jiki, yi motsa jiki, kuma yi barci mai kyau. Wanke hannuwanka da sabulu. Yi alluran rigakafi. Idan ba ka ji daɗi, je asibiti. Kula da lafiyar hankali shima yana da muhimmanci - yi magana da wanda ka amince da shi idan kana jin damuwa. Taimako yana nan.",
			category: "health",
			language: "ha",
			summary:  "Muhimman hanyoyin kula da lafiyar jiki da hankali",
			tags:     []string{"lafiya", "kula da jiki", "tsafta", "hankali"},
		},
	}

	for _, c := range content {
		tagsJSON, _ := json.Marshal(c.tags)
		db.Exec(
			"INSERT INTO content (title, body, category, language, tags, summary) VALUES (?, ?, ?, ?, ?, ?)",
			c.title, c.body, c.category, c.language, string(tagsJSON), c.summary,
		)
	}

	// Seed emergency alerts
	var alertCount int
	db.QueryRow("SELECT COUNT(*) FROM emergency_alerts").Scan(&alertCount)
	if alertCount > 0 {
		return
	}

	alerts := []struct {
		title, body, severity, regions, expiresAt string
	}{
		{
			title:     "Cyclone Season Alert",
			body:      "Cyclone season is approaching coastal regions. Prepare your emergency kit, know evacuation routes, and stay tuned to local radio for updates. Secure loose items around your home.",
			severity:  "warning",
			regions:   `["Coastal", "Low-lying areas"]`,
			expiresAt: time.Now().AddDate(0, 3, 0).Format(time.RFC3339),
		},
		{
			title:     "Cholera Prevention",
			body:      "Cholera outbreaks reported in some regions. Boil all drinking water, wash hands frequently with soap, and seek medical help immediately if you experience severe diarrhea and vomiting.",
			severity:  "high",
			regions:   `["High-density areas", "Flood-prone areas"]`,
			expiresAt: time.Now().AddDate(0, 1, 0).Format(time.RFC3339),
		},
		{
			title:     "Heatwave Advisory",
			body:      "Extreme temperatures expected. Stay hydrated, avoid direct sun during peak hours (11am-3pm), check on elderly neighbors, and never leave children in parked vehicles.",
			severity:  "info",
			regions:   `["All regions"]`,
			expiresAt: time.Now().AddDate(0, 0, 14).Format(time.RFC3339),
		},
	}

	for _, a := range alerts {
		db.Exec(
			"INSERT INTO emergency_alerts (title, body, severity, regions, created_at, expires_at) VALUES (?, ?, ?, ?, datetime('now'), ?)",
			a.title, a.body, a.severity, a.regions, a.expiresAt,
		)
	}
}

// --- Handlers ---

func handleGetContent(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	lang := r.URL.Query().Get("language")
	category := r.URL.Query().Get("category")

	query := "SELECT id, title, body, category, language, tags, summary, created_at FROM content WHERE 1=1"
	var args []interface{}

	if lang != "" {
		query += " AND language = ?"
		args = append(args, lang)
	}
	if category != "" {
		query += " AND category = ?"
		args = append(args, category)
	}

	query += " ORDER BY created_at DESC"

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var content []Content
	for rows.Next() {
		var c Content
		var tagsJSON string
		if err := rows.Scan(&c.ID, &c.Title, &c.Body, &c.Category, &c.Language, &tagsJSON, &c.Summary, &c.CreatedAt); err != nil {
			continue
		}
		json.Unmarshal([]byte(tagsJSON), &c.Tags)
		content = append(content, c)
	}

	json.NewEncoder(w).Encode(content)
}

func handleGetContentByID(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	id := r.PathValue("id")
	var c Content
	var tagsJSON string
	err := db.QueryRow("SELECT id, title, body, category, language, tags, summary, created_at FROM content WHERE id = ?", id).
		Scan(&c.ID, &c.Title, &c.Body, &c.Category, &c.Language, &tagsJSON, &c.Summary, &c.CreatedAt)
	if err != nil {
		http.Error(w, "Content not found", http.StatusNotFound)
		return
	}
	json.Unmarshal([]byte(tagsJSON), &c.Tags)
	json.NewEncoder(w).Encode(c)
}

func handleGetContentByCategory(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	category := r.PathValue("category")
	lang := r.URL.Query().Get("language")

	query := "SELECT id, title, body, category, language, tags, summary, created_at FROM content WHERE category = ?"
	var args []interface{}
	args = append(args, category)

	if lang != "" {
		query += " AND language = ?"
		args = append(args, lang)
	}

	query += " ORDER BY created_at DESC"

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var content []Content
	for rows.Next() {
		var c Content
		var tagsJSON string
		if err := rows.Scan(&c.ID, &c.Title, &c.Body, &c.Category, &c.Language, &tagsJSON, &c.Summary, &c.CreatedAt); err != nil {
			continue
		}
		json.Unmarshal([]byte(tagsJSON), &c.Tags)
		content = append(content, c)
	}

	json.NewEncoder(w).Encode(content)
}

func handleSearchContent(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	q := r.URL.Query().Get("q")
	if q == "" {
		json.NewEncoder(w).Encode([]Content{})
		return
	}

	rows, err := db.Query(
		"SELECT id, title, body, category, language, tags, summary, created_at FROM content WHERE title LIKE ? OR body LIKE ? OR summary LIKE ? ORDER BY created_at DESC",
		"%"+q+"%", "%"+q+"%", "%"+q+"%",
	)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var content []Content
	for rows.Next() {
		var c Content
		var tagsJSON string
		if err := rows.Scan(&c.ID, &c.Title, &c.Body, &c.Category, &c.Language, &tagsJSON, &c.Summary, &c.CreatedAt); err != nil {
			continue
		}
		json.Unmarshal([]byte(tagsJSON), &c.Tags)
		content = append(content, c)
	}

	json.NewEncoder(w).Encode(content)
}

func handleAIAsk(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	var req struct {
		Question string `json:"question"`
		Language string `json:"language"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if req.Question == "" {
		http.Error(w, "Question is required", http.StatusBadRequest)
		return
	}

	// Search content for relevant answers
	rows, err := db.Query(
		"SELECT title, body, category, language FROM content WHERE (title LIKE ? OR body LIKE ?) AND language = ? LIMIT 3",
		"%"+req.Question+"%", "%"+req.Question+"%", req.Language,
	)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var relevantContent []Content
	for rows.Next() {
		var c Content
		if err := rows.Scan(&c.Title, &c.Body, &c.Category, &c.Language); err != nil {
			continue
		}
		relevantContent = append(relevantContent, c)
	}

	// Build response
	var response string
	if len(relevantContent) > 0 {
		response = "Based on our information:\n\n"
		for _, c := range relevantContent {
			response += fmt.Sprintf("**%s** (%s):\n%s\n\n", c.Title, c.Category, c.Body)
		}
		response += "For more information, browse our content library or contact local community health workers."
	} else {
		response = getDefaultResponse(req.Language)
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"answer":  response,
		"matched": len(relevantContent) > 0,
	})
}

func getDefaultResponse(lang string) string {
	responses := map[string]string{
		"en": "I don't have specific information on that topic yet. Try searching our content library for health, education, legal rights, or emergency preparedness. You can also contact local community health workers or NGOs for assistance.",
		"sw": "Sina taarifa maalum kuhusu somo hilo bado. Jaribu kutafuta katika maktaba yetu ya maudhui kwa afya, elimu, haki za kisheria, au maandalizi ya dharura. Unaweza pia kuwasiliana na wafanyakazi wa afya ya jamii au mashirika yasiyo ya kiserikali kwa usaidizi.",
		"fr": "Je n'ai pas encore d'informations spécifiques sur ce sujet. Essayez de parcourir notre bibliothèque de contenu pour la santé, l'éducation, les droits légaux ou la préparation aux urgences. Vous pouvez également contacter des agents de santé communautaires ou des ONG pour obtenir de l'aide.",
		"es": "Todavía no tengo información específica sobre ese tema. Intente explorar nuestra biblioteca de contenido sobre salud, educación, derechos legales o preparación para emergencias. También puede contactar a trabajadores de salud comunitarios u ONG para obtener ayuda.",
		"ar": "ليس لدي معلومات محددة حول هذا الموضوع بعد. حاول تصفح مكتبة المحتوى الخاصة بنا للصحة أو التعليم أو الحقوق القانونية أو الاستعداد للطوارئ. يمكنك أيضًا الاتصال بالعاملين الصحيين المجتمعيين أو المنظمات غير الحكومية للحصول على المساعدة.",
		"ha": "Ba ni da takamaiman bayani kan wannan batu tukuna. Gwada bincika ɗakin karatu na mu don lafiya, ilimi, hakkokin shari'a, ko shirye-shiryen gaggawa. Hakanan zaka iya tuntuɓar ma'aikatan kiwon lafiya na al'umma ko ƙungiyoyi masu zaman kansu don taimako.",
	}

	if resp, ok := responses[lang]; ok {
		return resp
	}
	return responses["en"]
}

func handleGetQuestions(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	lang := r.URL.Query().Get("language")
	category := r.URL.Query().Get("category")

	query := "SELECT id, question, answer, language, category, created_at FROM questions WHERE 1=1"
	var args []interface{}

	if lang != "" {
		query += " AND language = ?"
		args = append(args, lang)
	}
	if category != "" {
		query += " AND category = ?"
		args = append(args, category)
	}

	query += " ORDER BY created_at DESC LIMIT 50"

	rows, err := db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var questions []Question
	for rows.Next() {
		var q Question
		if err := rows.Scan(&q.ID, &q.Question, &q.Answer, &q.Language, &q.Category, &q.CreatedAt); err != nil {
			continue
		}
		questions = append(questions, q)
	}

	json.NewEncoder(w).Encode(questions)
}

func handlePostQuestion(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	var q Question
	if err := json.NewDecoder(r.Body).Decode(&q); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if q.Question == "" {
		http.Error(w, "Question is required", http.StatusBadRequest)
		return
	}
	if q.Language == "" {
		q.Language = "en"
	}
	if q.Category == "" {
		q.Category = "general"
	}

	result, err := db.Exec("INSERT INTO questions (question, language, category) VALUES (?, ?, ?)", q.Question, q.Language, q.Category)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	id, _ := result.LastInsertId()
	q.ID = int(id)
	q.CreatedAt = time.Now().Format(time.RFC3339)

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(q)
}

func handlePostAnswer(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	id := r.PathValue("id")
	var req struct {
		Answer string `json:"answer"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	if req.Answer == "" {
		http.Error(w, "Answer is required", http.StatusBadRequest)
		return
	}

	_, err := db.Exec("UPDATE questions SET answer = ? WHERE id = ?", req.Answer, id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func handleGetAlerts(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	rows, err := db.Query("SELECT id, title, body, severity, regions, created_at, expires_at FROM emergency_alerts ORDER BY created_at DESC")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var alerts []EmergencyAlert
	for rows.Next() {
		var a EmergencyAlert
		var regionsJSON string
		if err := rows.Scan(&a.ID, &a.Title, &a.Body, &a.Severity, &regionsJSON, &a.CreatedAt, &a.ExpiresAt); err != nil {
			continue
		}
		json.Unmarshal([]byte(regionsJSON), &a.Regions)
		alerts = append(alerts, a)
	}

	json.NewEncoder(w).Encode(alerts)
}

func handleGetActiveAlerts(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	rows, err := db.Query(
		"SELECT id, title, body, severity, regions, created_at, expires_at FROM emergency_alerts WHERE expires_at > datetime('now') ORDER BY created_at DESC",
	)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var alerts []EmergencyAlert
	for rows.Next() {
		var a EmergencyAlert
		var regionsJSON string
		if err := rows.Scan(&a.ID, &a.Title, &a.Body, &a.Severity, &regionsJSON, &a.CreatedAt, &a.ExpiresAt); err != nil {
			continue
		}
		json.Unmarshal([]byte(regionsJSON), &a.Regions)
		alerts = append(alerts, a)
	}

	json.NewEncoder(w).Encode(alerts)
}

func handleGetLanguages(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	rows, err := db.Query("SELECT code, name FROM languages ORDER BY name")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var languages []Language
	for rows.Next() {
		var l Language
		if err := rows.Scan(&l.Code, &l.Name); err != nil {
			continue
		}
		languages = append(languages, l)
	}

	json.NewEncoder(w).Encode(languages)
}
