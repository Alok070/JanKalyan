"""
Seed data for 10 high-impact welfare schemes.

All data is grounded in official myScheme.gov.in / ministry pages.
Each scheme has trilingual (EN / HI / TA) content.
"""

from app.models import SchemeRecord, SchemeEligibility

SCHEMES: list[SchemeRecord] = [
    # ------------------------------------------------------------------
    # 1. PM-KISAN
    # ------------------------------------------------------------------
    SchemeRecord(
        id="pm_kisan",
        name_en="PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        name_hi="पीएम-किसान (प्रधानमंत्री किसान सम्मान निधि)",
        name_ta="பிஎம்-கிசான் (பிரதான் மந்திரி கிசான் சம்மான் நிதி)",
        category="agriculture",
        description_en="Income support of ₹6,000 per year in three installments to small and marginal farmer families.",
        description_hi="छोटे और सीमांत किसान परिवारों को तीन किस्तों में ₹6,000 प्रति वर्ष की आय सहायता।",
        description_ta="சிறு மற்றும் குறு விவசாயி குடும்பங்களுக்கு ஆண்டுக்கு ₹6,000 வருமான உதவி மூன்று தவணைகளில்.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=120,
            gender=["male", "female", "other"],
            occupations=["farmer"],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Must own cultivable land", "Not an income-tax payer"],
        ),
        eligibility_summary_en="Any farmer family with cultivable land. Not for income-tax payers or government employees.",
        eligibility_summary_hi="खेती योग्य जमीन वाला कोई भी किसान परिवार। आयकर दाताओं या सरकारी कर्मचारियों के लिए नहीं।",
        eligibility_summary_ta="பயிரிடக்கூடிய நிலம் உள்ள எந்த விவசாயி குடும்பமும். வருமான வரி செலுத்துபவர்களுக்கு அல்ல.",
        documents_en=["Aadhaar Card", "Bank Account (linked to Aadhaar)", "Land ownership records", "Mobile number"],
        documents_hi=["आधार कार्ड", "बैंक खाता (आधार से जुड़ा)", "भूमि स्वामित्व रिकॉर्ड", "मोबाइल नंबर"],
        documents_ta=["ஆதார் அட்டை", "வங்கி கணக்கு (ஆதாருடன் இணைக்கப்பட்டது)", "நில உரிமை ஆவணங்கள்", "மொபைல் எண்"],
        benefits_en="₹6,000 per year in 3 installments of ₹2,000 each, directly to bank account.",
        benefits_hi="₹6,000 प्रति वर्ष, ₹2,000 की 3 किस्तों में, सीधे बैंक खाते में।",
        benefits_ta="ஆண்டுக்கு ₹6,000, ₹2,000 வீதம் 3 தவணைகளில், நேரடியாக வங்கி கணக்கில்.",
        official_url="https://pmkisan.gov.in/",
        source="pmkisan.gov.in",
    ),

    # ------------------------------------------------------------------
    # 2. Ayushman Bharat (PM-JAY)
    # ------------------------------------------------------------------
    SchemeRecord(
        id="ayushman_bharat",
        name_en="Ayushman Bharat (PM-JAY)",
        name_hi="आयुष्मान भारत (पीएम-जय)",
        name_ta="ஆயுஷ்மான் பாரத் (பிஎம்-ஜே.ஏ.ஒய்)",
        category="health",
        description_en="Free health insurance cover of ₹5 lakh per family per year for secondary and tertiary hospitalization.",
        description_hi="माध्यमिक और तृतीयक अस्पताल भर्ती के लिए प्रति परिवार प्रति वर्ष ₹5 लाख तक का मुफ्त स्वास्थ्य बीमा।",
        description_ta="இரண்டாம் மற்றும் மூன்றாம் நிலை மருத்துமனை சிகிச்சைக்கு ஒரு குடும்பத்திற்கு ஆண்டுக்கு ₹5 லட்சம் இலவச மருத்துவ காப்பீடு.",
        eligibility=SchemeEligibility(
            min_age=0, max_age=120,
            gender=["male", "female", "other"],
            occupations=[],
            max_monthly_income=25000,
            states=[],
            categories=["BPL", "deprived"],
            extra_conditions=["Family must be in SECC 2011 database or state equivalent list"],
        ),
        eligibility_summary_en="Low-income families listed in SECC 2011 database. No age limit. Covers up to ₹5 lakh/year.",
        eligibility_summary_hi="SECC 2011 डेटाबेस में सूचीबद्ध कम आय वाले परिवार। कोई आयु सीमा नहीं। ₹5 लाख/वर्ष तक कवर।",
        eligibility_summary_ta="SECC 2011 தரவுத்தளத்தில் பட்டியலிடப்பட்ட குறைந்த வருமான குடும்பங்கள். வயது வரம்பு இல்லை. ₹5 லட்சம்/ஆண்டு வரை.",
        documents_en=["Aadhaar Card", "Ration Card / SECC list inclusion", "Mobile number", "Family ID (if applicable)"],
        documents_hi=["आधार कार्ड", "राशन कार्ड / SECC सूची", "मोबाइल नंबर", "परिवार आईडी (यदि लागू हो)"],
        documents_ta=["ஆதார் அட்டை", "ரேஷன் கார்டு / SECC பட்டியல்", "மொபைல் எண்", "குடும்ப அடையாள அட்டை (பொருந்தினால்)"],
        benefits_en="Up to ₹5 lakh per family per year for hospitalization. Cashless treatment at empanelled hospitals.",
        benefits_hi="अस्पताल भर्ती के लिए प्रति परिवार प्रति वर्ष ₹5 लाख तक। सूचीबद्ध अस्पतालों में कैशलेस इलाज।",
        benefits_ta="மருத்துவமனையில் சேர்க்கைக்கு குடும்பத்திற்கு ஆண்டுக்கு ₹5 லட்சம் வரை. பட்டியலிடப்பட்ட மருத்துவமனைகளில் பணமில்லா சிகிச்சை.",
        official_url="https://pmjay.gov.in/",
        source="pmjay.gov.in",
    ),

    # ------------------------------------------------------------------
    # 3. PMAY (Pradhan Mantri Awas Yojana)
    # ------------------------------------------------------------------
    SchemeRecord(
        id="pmay",
        name_en="PMAY (Pradhan Mantri Awas Yojana)",
        name_hi="पीएमएवाई (प्रधानमंत्री आवास योजना)",
        name_ta="பிஎம்ஏஒய் (பிரதான் மந்திரி ஆவாஸ் யோஜனா)",
        category="housing",
        description_en="Financial assistance for building or upgrading a pucca house for homeless and those living in kutcha houses.",
        description_hi="बेघर और कच्चे घर में रहने वालों को पक्का घर बनाने या उन्नत करने के लिए वित्तीय सहायता।",
        description_ta="வீடற்றவர்களுக்கும் குச்சா வீடுகளில் வசிப்பவர்களுக்கும் பக்கா வீடு கட்ட நிதி உதவி.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=120,
            gender=["male", "female", "other"],
            occupations=[],
            max_monthly_income=25000,
            states=[],
            categories=["BPL", "EWS", "LIG"],
            extra_conditions=["Should not own a pucca house anywhere in India", "Priority to SC/ST, minorities, widows"],
        ),
        eligibility_summary_en="Homeless or kutcha house owners. EWS/LIG income category. Should not own a pucca house.",
        eligibility_summary_hi="बेघर या कच्चे घर के मालिक। EWS/LIG आय वर्ग। कहीं भी पक्का मकान नहीं होना चाहिए।",
        eligibility_summary_ta="வீடற்றவர்கள் அல்லது குச்சா வீட்டு உரிமையாளர்கள். EWS/LIG வருமான பிரிவு.",
        documents_en=["Aadhaar Card", "Income Certificate", "BPL/Ration Card", "Bank Account", "Land documents (for rural)", "Photograph"],
        documents_hi=["आधार कार्ड", "आय प्रमाण पत्र", "बीपीएल/राशन कार्ड", "बैंक खाता", "भूमि दस्तावेज (ग्रामीण के लिए)", "फोटो"],
        documents_ta=["ஆதார் அட்டை", "வருமானச் சான்றிதழ்", "BPL/ரேஷன் கார்டு", "வங்கி கணக்கு", "நில ஆவணங்கள் (கிராமப்புறத்திற்கு)", "புகைப்படம்"],
        benefits_en="₹1.20 lakh (plain area) to ₹1.30 lakh (hilly area) for new house construction under Gramin. Urban: interest subsidy up to ₹2.67 lakh.",
        benefits_hi="नए घर के निर्माण के लिए ₹1.20 लाख (मैदानी) से ₹1.30 लाख (पहाड़ी)। शहरी: ₹2.67 लाख तक ब्याज सब्सिडी।",
        benefits_ta="புதிய வீட்டுக்கு ₹1.20 லட்சம் (சமவெளி) முதல் ₹1.30 லட்சம் (மலைப்பகுதி). நகர்ப்புறம்: ₹2.67 லட்சம் வரை வட்டி மானியம்.",
        official_url="https://pmaymis.gov.in/",
        source="pmaymis.gov.in",
    ),

    # ------------------------------------------------------------------
    # 4. Ujjwala Yojana
    # ------------------------------------------------------------------
    SchemeRecord(
        id="ujjwala",
        name_en="Pradhan Mantri Ujjwala Yojana (PMUY)",
        name_hi="प्रधानमंत्री उज्ज्वला योजना (पीएमयूवाई)",
        name_ta="பிரதான் மந்திரி உஜ்வலா யோஜனா (பிஎம்யுஒய்)",
        category="energy",
        description_en="Free LPG connection to women from BPL households to replace unclean cooking fuels.",
        description_hi="अशुद्ध खाना पकाने के ईंधन को बदलने के लिए बीपीएल परिवारों की महिलाओं को मुफ्त एलपीजी कनेक्शन।",
        description_ta="சுத்தமற்ற சமையல் எரிபொருளை மாற்ற BPL குடும்பங்களின் பெண்களுக்கு இலவச எல்பிஜி இணைப்பு.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=120,
            gender=["female"],
            occupations=[],
            max_monthly_income=10000,
            states=[],
            categories=["BPL"],
            extra_conditions=["Woman of the household", "No existing LPG connection in the household"],
        ),
        eligibility_summary_en="Adult women from BPL households. No existing LPG connection in the family.",
        eligibility_summary_hi="बीपीएल परिवारों की वयस्क महिलाएं। परिवार में कोई मौजूदा एलपीजी कनेक्शन नहीं।",
        eligibility_summary_ta="BPL குடும்பங்களின் வயது வந்த பெண்கள். குடும்பத்தில் ஏற்கனவே எல்பிஜி இணைப்பு இல்லை.",
        documents_en=["Aadhaar Card", "BPL Ration Card", "Bank Account", "Passport-size photograph", "Address proof"],
        documents_hi=["आधार कार्ड", "बीपीएल राशन कार्ड", "बैंक खाता", "पासपोर्ट साइज फोटो", "पता प्रमाण"],
        documents_ta=["ஆதார் அட்டை", "BPL ரேஷன் கார்டு", "வங்கி கணக்கு", "பாஸ்போர்ட் அளவு புகைப்படம்", "முகவரி சான்று"],
        benefits_en="Free LPG connection (₹1,600 subsidy). Free first refill and stove under Ujjwala 2.0.",
        benefits_hi="मुफ्त एलपीजी कनेक्शन (₹1,600 सब्सिडी)। उज्ज्वला 2.0 के तहत पहली रिफिल और चूल्हा मुफ्त।",
        benefits_ta="இலவச எல்பிஜி இணைப்பு (₹1,600 மானியம்). உஜ்வலா 2.0 கீழ் முதல் ரீஃபில் மற்றும் அடுப்பு இலவசம்.",
        official_url="https://www.pmuy.gov.in/",
        source="pmuy.gov.in",
    ),

    # ------------------------------------------------------------------
    # 5. MGNREGA
    # ------------------------------------------------------------------
    SchemeRecord(
        id="mgnrega",
        name_en="MGNREGA (Mahatma Gandhi National Rural Employment Guarantee Act)",
        name_hi="मनरेगा (महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम)",
        name_ta="மகாத்மா காந்தி தேசிய ஊரக வேலைவாய்ப்பு உறுதியளிப்புச் சட்டம் (MGNREGA)",
        category="employment",
        description_en="Guarantees 100 days of wage employment per year to every rural household whose adult members volunteer to do unskilled manual work.",
        description_hi="हर ग्रामीण परिवार को जिसके वयस्क सदस्य अकुशल शारीरिक काम करने को तैयार हैं, प्रति वर्ष 100 दिन वेतन रोजगार की गारंटी।",
        description_ta="திறனற்ற உடல் உழைப்பு செய்ய முன்வரும் வயது வந்த உறுப்பினர்கள் கொண்ட ஒவ்வொரு கிராமப்புற குடும்பத்திற்கும் ஆண்டுக்கு 100 நாள் ஊதிய வேலை உத்தரவாதம்.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=120,
            gender=["male", "female", "other"],
            occupations=["laborer", "farmer", "other"],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Must be a rural resident", "Willing to do unskilled manual work"],
        ),
        eligibility_summary_en="Any adult rural resident willing to do unskilled manual work. No income limit.",
        eligibility_summary_hi="अकुशल शारीरिक काम करने के इच्छुक कोई भी वयस्क ग्रामीण निवासी। कोई आय सीमा नहीं।",
        eligibility_summary_ta="திறனற்ற உடல் உழைப்பு செய்ய விரும்பும் எந்த வயது வந்த கிராமப்புற குடியிருப்பாளரும். வருமான வரம்பு இல்லை.",
        documents_en=["Aadhaar Card", "Job Card (issued by Gram Panchayat)", "Bank Account / Post Office Account", "Photograph"],
        documents_hi=["आधार कार्ड", "जॉब कार्ड (ग्राम पंचायत द्वारा जारी)", "बैंक खाता / डाकघर खाता", "फोटो"],
        documents_ta=["ஆதார் அட்டை", "வேலை அட்டை (கிராம பஞ்சாயத்து வழங்கியது)", "வங்கி கணக்கு / தபால் அலுவலக கணக்கு", "புகைப்படம்"],
        benefits_en="100 days of guaranteed wage employment per year. Wages vary by state (₹200–₹350/day). Unemployment allowance if work not provided within 15 days.",
        benefits_hi="प्रति वर्ष 100 दिन गारंटीशुदा वेतन रोजगार। मजदूरी राज्य अनुसार (₹200–₹350/दिन)।",
        benefits_ta="ஆண்டுக்கு 100 நாள் உத்தரவாத ஊதிய வேலை. ஊதியம் மாநிலத்தைப் பொறுத்தது (₹200–₹350/நாள்).",
        official_url="https://nrega.nic.in/",
        source="nrega.nic.in",
    ),

    # ------------------------------------------------------------------
    # 6. Sukanya Samriddhi Yojana
    # ------------------------------------------------------------------
    SchemeRecord(
        id="sukanya_samriddhi",
        name_en="Sukanya Samriddhi Yojana (SSY)",
        name_hi="सुकन्या समृद्धि योजना (एसएसवाई)",
        name_ta="சுகன்யா சம்ரிதி யோஜனா (SSY)",
        category="savings",
        description_en="Savings scheme for the girl child. High interest rate, tax benefits, and maturity at age 21.",
        description_hi="बालिका के लिए बचत योजना। उच्च ब्याज दर, कर लाभ, और 21 वर्ष की आयु में परिपक्वता।",
        description_ta="பெண் குழந்தைக்கான சேமிப்புத் திட்டம். அதிக வட்டி விகிதம், வரி சலுகைகள், 21 வயதில் முதிர்வு.",
        eligibility=SchemeEligibility(
            min_age=0, max_age=10,
            gender=["female"],
            occupations=[],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Account opened by parent/guardian for girl child below 10 years", "Maximum 2 accounts per family"],
        ),
        eligibility_summary_en="Girl child below 10 years. Account opened by parent/guardian. Max 2 accounts per family.",
        eligibility_summary_hi="10 वर्ष से कम उम्र की बालिका। माता-पिता/अभिभावक द्वारा खाता खोला जाता है। प्रति परिवार अधिकतम 2 खाते।",
        eligibility_summary_ta="10 வயதிற்குட்பட்ட பெண் குழந்தை. பெற்றோர்/பாதுகாவலர் கணக்கு தொடங்குவார். ஒரு குடும்பத்திற்கு அதிகபட்சம் 2 கணக்குகள்.",
        documents_en=["Birth Certificate of girl child", "Aadhaar Card (parent & child)", "Address proof", "Photograph of parent/guardian"],
        documents_hi=["बालिका का जन्म प्रमाण पत्र", "आधार कार्ड (माता-पिता और बालिका)", "पता प्रमाण", "माता-पिता/अभिभावक की फोटो"],
        documents_ta=["பெண் குழந்தையின் பிறப்புச் சான்றிதழ்", "ஆதார் அட்டை (பெற்றோர் & குழந்தை)", "முகவரி சான்று", "பெற்றோர்/பாதுகாவலரின் புகைப்படம்"],
        benefits_en="Interest rate ~8.2% p.a. (government-set). Tax-free under Section 80C. Maturity at 21 years. Partial withdrawal at 18 for education.",
        benefits_hi="ब्याज दर ~8.2% प्रति वर्ष। धारा 80C के तहत कर-मुक्त। 21 वर्ष में परिपक्वता। 18 पर शिक्षा हेतु आंशिक निकासी।",
        benefits_ta="வட்டி விகிதம் ~8.2% ஆண்டுக்கு. பிரிவு 80C கீழ் வரி இல்லை. 21 வயதில் முதிர்வு. 18 வயதில் கல்விக்கு பகுதி திரும்பப்பெறுதல்.",
        official_url="https://www.nsiindia.gov.in/InternalPage.aspx?Id_Pk=89",
        source="nsiindia.gov.in",
    ),

    # ------------------------------------------------------------------
    # 7. Atal Pension Yojana
    # ------------------------------------------------------------------
    SchemeRecord(
        id="atal_pension",
        name_en="Atal Pension Yojana (APY)",
        name_hi="अटल पेंशन योजना (एपीवाई)",
        name_ta="அடல் பென்ஷன் யோஜனா (APY)",
        category="pension",
        description_en="Guaranteed minimum pension of ₹1,000 to ₹5,000/month after age 60 for unorganized sector workers.",
        description_hi="असंगठित क्षेत्र के श्रमिकों को 60 वर्ष की आयु के बाद ₹1,000 से ₹5,000/माह की गारंटीशुदा न्यूनतम पेंशन।",
        description_ta="60 வயதிற்குப் பிறகு அமைப்புசாரா தொழிலாளர்களுக்கு ₹1,000 முதல் ₹5,000/மாதம் உத்தரவாத குறைந்தபட்ச ஓய்வூதியம்.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=40,
            gender=["male", "female", "other"],
            occupations=["laborer", "farmer", "homemaker", "other"],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Must have a savings bank account", "Not a member of any statutory social security scheme", "Age 18–40 years"],
        ),
        eligibility_summary_en="Age 18–40. Unorganized sector workers. Must have bank account. Not covered by statutory pension.",
        eligibility_summary_hi="आयु 18–40। असंगठित क्षेत्र के कामगार। बैंक खाता आवश्यक। वैधानिक पेंशन से कवर नहीं।",
        eligibility_summary_ta="வயது 18–40. அமைப்புசாரா தொழிலாளர்கள். வங்கி கணக்கு தேவை. சட்டரீதியான ஓய்வூதியத்தில் சேராதவர்.",
        documents_en=["Aadhaar Card", "Bank Account", "Mobile number linked to bank"],
        documents_hi=["आधार कार्ड", "बैंक खाता", "बैंक से जुड़ा मोबाइल नंबर"],
        documents_ta=["ஆதார் அட்டை", "வங்கி கணக்கு", "வங்கியுடன் இணைக்கப்பட்ட மொபைல் எண்"],
        benefits_en="Monthly pension ₹1,000–₹5,000 after age 60 (based on contribution). Spouse gets same pension after subscriber's death.",
        benefits_hi="60 वर्ष के बाद मासिक पेंशन ₹1,000–₹5,000 (अंशदान के आधार पर)। ग्राहक की मृत्यु के बाद पत्नी/पति को समान पेंशन।",
        benefits_ta="60 வயதிற்குப் பிறகு மாதாந்திர ஓய்வூதியம் ₹1,000–₹5,000. சந்தாதாரர் இறப்பிற்குப் பிறகு வாழ்க்கைத்துணைக்கு அதே ஓய்வூதியம்.",
        official_url="https://www.npscra.nsdl.co.in/scheme-details.php",
        source="npscra.nsdl.co.in",
    ),

    # ------------------------------------------------------------------
    # 8. PM Vishwakarma
    # ------------------------------------------------------------------
    SchemeRecord(
        id="pm_vishwakarma",
        name_en="PM Vishwakarma Yojana",
        name_hi="पीएम विश्वकर्मा योजना",
        name_ta="பிஎம் விஸ்வகர்மா யோஜனா",
        category="skill_development",
        description_en="End-to-end support for traditional artisans and craftspeople through training, tools, credit, and market linkage.",
        description_hi="प्रशिक्षण, उपकरण, ऋण और बाजार जोड़ने के माध्यम से पारंपरिक कारीगरों और शिल्पकारों को संपूर्ण सहायता।",
        description_ta="பயிற்சி, கருவிகள், கடன் மற்றும் சந்தை இணைப்பு மூலம் பாரம்பரிய கைவினைஞர்களுக்கு முழுமையான ஆதரவு.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=120,
            gender=["male", "female", "other"],
            occupations=["artisan", "other"],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Must be engaged in one of the 18 listed traditional trades", "e.g., carpenter, blacksmith, goldsmith, potter, weaver, tailor, cobbler"],
        ),
        eligibility_summary_en="Traditional artisans/craftspeople in 18 listed trades (carpenter, blacksmith, potter, weaver, tailor, etc.).",
        eligibility_summary_hi="18 सूचीबद्ध पारंपरिक व्यापारों में कारीगर/शिल्पकार (बढ़ई, लोहार, कुम्हार, बुनकर, दर्जी आदि)।",
        eligibility_summary_ta="18 பட்டியலிடப்பட்ட பாரம்பரிய தொழில்களில் கைவினைஞர்கள் (தச்சர், கொல்லர், குயவர், நெசவாளர், தையல்காரர் போன்றவர்கள்).",
        documents_en=["Aadhaar Card", "Bank Account", "Mobile number", "Caste Certificate (if applicable)", "Proof of trade (self-declaration or Gram Panchayat certificate)"],
        documents_hi=["आधार कार्ड", "बैंक खाता", "मोबाइल नंबर", "जाति प्रमाण पत्र (यदि लागू)", "व्यापार का प्रमाण (स्व-घोषणा या ग्राम पंचायत प्रमाण पत्र)"],
        documents_ta=["ஆதார் அட்டை", "வங்கி கணக்கு", "மொபைல் எண்", "சாதிச் சான்றிதழ் (பொருந்தினால்)", "தொழில் சான்று (சுய-அறிவிப்பு அல்லது கிராம பஞ்சாயத்து சான்றிதழ்)"],
        benefits_en="Skills training (5–15 days with ₹500/day stipend), toolkit worth ₹15,000, collateral-free loan up to ₹3 lakh at 5% interest, PM Vishwakarma certificate & ID.",
        benefits_hi="कौशल प्रशिक्षण (5-15 दिन, ₹500/दिन भत्ता), ₹15,000 का टूलकिट, 5% ब्याज पर ₹3 लाख तक बिना गारंटी ऋण।",
        benefits_ta="திறன் பயிற்சி (5-15 நாள், ₹500/நாள் உதவித்தொகை), ₹15,000 மதிப்புள்ள கருவித்தொகுப்பு, 5% வட்டியில் ₹3 லட்சம் வரை ஈட்டில்லா கடன்.",
        official_url="https://pmvishwakarma.gov.in/",
        source="pmvishwakarma.gov.in",
    ),

    # ------------------------------------------------------------------
    # 9. Kisan Credit Card (KCC)
    # ------------------------------------------------------------------
    SchemeRecord(
        id="kisan_credit_card",
        name_en="Kisan Credit Card (KCC)",
        name_hi="किसान क्रेडिट कार्ड (केसीसी)",
        name_ta="கிசான் கிரெடிட் கார்டு (KCC)",
        category="agriculture",
        description_en="Credit facility for farmers to meet agricultural and allied expenses at subsidized interest rates.",
        description_hi="किसानों को कृषि और संबद्ध खर्चों को पूरा करने के लिए रियायती ब्याज दरों पर ऋण सुविधा।",
        description_ta="விவசாயிகளுக்கு வேளாண்மை மற்றும் தொடர்புடைய செலவுகளை சமாளிக்க மானிய வட்டி விகிதத்தில் கடன் வசதி.",
        eligibility=SchemeEligibility(
            min_age=18, max_age=75,
            gender=["male", "female", "other"],
            occupations=["farmer"],
            max_monthly_income=0,
            states=[],
            categories=[],
            extra_conditions=["Individual farmers, joint borrowers, tenant farmers, sharecroppers", "Also available for fisheries and animal husbandry"],
        ),
        eligibility_summary_en="All farmers — owner cultivators, tenant farmers, sharecroppers. Also for fisheries and animal husbandry.",
        eligibility_summary_hi="सभी किसान — मालिक, किरायेदार, बटाईदार। मत्स्य पालन और पशुपालन के लिए भी।",
        eligibility_summary_ta="அனைத்து விவசாயிகள் — உரிமையாளர், குத்தகைதாரர், பங்கு பயிர்ச்செய்பவர்கள். மீன் வளர்ப்பு மற்றும் கால்நடை வளர்ப்புக்கும்.",
        documents_en=["Aadhaar Card", "Land records / tenancy agreement", "Bank Account", "Passport-size photograph", "Crop sowing certificate (from Patwari/Revenue officer)"],
        documents_hi=["आधार कार्ड", "भूमि रिकॉर्ड / किरायेदारी अनुबंध", "बैंक खाता", "पासपोर्ट साइज फोटो", "फसल बुवाई प्रमाण पत्र"],
        documents_ta=["ஆதார் அட்டை", "நில ஆவணங்கள் / குத்தகை ஒப்பந்தம்", "வங்கி கணக்கு", "பாஸ்போர்ட் அளவு புகைப்படம்", "பயிர் விதைப்பு சான்றிதழ்"],
        benefits_en="Credit up to ₹3 lakh at 4% interest (with subsidy). Crop insurance cover included. Flexible repayment.",
        benefits_hi="4% ब्याज पर ₹3 लाख तक ऋण (सब्सिडी सहित)। फसल बीमा कवर शामिल।",
        benefits_ta="4% வட்டியில் ₹3 லட்சம் வரை கடன் (மானியத்துடன்). பயிர் காப்பீடு உள்ளடக்கம்.",
        official_url="https://pmkisan.gov.in/KCC.aspx",
        source="pmkisan.gov.in",
    ),

    # ------------------------------------------------------------------
    # 10. Ladli Behna Yojana (Madhya Pradesh)
    # ------------------------------------------------------------------
    SchemeRecord(
        id="ladli_behna_mp",
        name_en="Ladli Behna Yojana (Madhya Pradesh)",
        name_hi="लाड़ली बहना योजना (मध्य प्रदेश)",
        name_ta="லாட்லி பெஹ்னா யோஜனா (மத்தியப் பிரதேசம்)",
        category="women_welfare",
        description_en="Monthly financial assistance of ₹1,250 to women of Madhya Pradesh for economic empowerment.",
        description_hi="आर्थिक सशक्तिकरण के लिए मध्य प्रदेश की महिलाओं को ₹1,250 प्रति माह वित्तीय सहायता।",
        description_ta="பொருளாதார மேம்பாட்டிற்காக மத்தியப் பிரதேச பெண்களுக்கு மாதம் ₹1,250 நிதி உதவி.",
        eligibility=SchemeEligibility(
            min_age=21, max_age=60,
            gender=["female"],
            occupations=[],
            max_monthly_income=25000,
            states=["madhya pradesh", "mp"],
            categories=[],
            extra_conditions=["Must be a married, divorced, or widowed woman", "Family annual income should not exceed ₹2.5 lakh", "Not an income-tax payer"],
        ),
        eligibility_summary_en="Women aged 21–60 in Madhya Pradesh. Family income below ₹2.5 lakh/year. Married/widowed/divorced.",
        eligibility_summary_hi="मध्य प्रदेश में 21–60 वर्ष की महिलाएं। पारिवारिक आय ₹2.5 लाख/वर्ष से कम। विवाहित/विधवा/तलाकशुदा।",
        eligibility_summary_ta="மத்தியப் பிரதேசத்தில் 21–60 வயது பெண்கள். குடும்ப வருமானம் ₹2.5 லட்சம்/ஆண்டுக்கு குறைவு. திருமணமான/விதவை/விவாகரத்தான.",
        documents_en=["Aadhaar Card", "Samagra ID (MP family ID)", "Bank Account", "Mobile number", "Passport-size photograph"],
        documents_hi=["आधार कार्ड", "समग्र आईडी", "बैंक खाता", "मोबाइल नंबर", "पासपोर्ट साइज फोटो"],
        documents_ta=["ஆதார் அட்டை", "சமக்ரா ஐடி", "வங்கி கணக்கு", "மொபைல் எண்", "பாஸ்போர்ட் அளவு புகைப்படம்"],
        benefits_en="₹1,250 per month (₹15,000 per year) directly to bank account.",
        benefits_hi="₹1,250 प्रति माह (₹15,000 प्रति वर्ष) सीधे बैंक खाते में।",
        benefits_ta="மாதம் ₹1,250 (ஆண்டுக்கு ₹15,000) நேரடியாக வங்கி கணக்கில்.",
        official_url="https://ladlibahna.mp.gov.in/",
        source="ladlibahna.mp.gov.in",
    ),
]
