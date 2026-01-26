# Marketing Lock Readiness Report

## Routes Table
URL | View | Template | Notes
--- | --- | --- | ---
/<lang>/ | core.views.home | templates/redirect | 
/<lang>/start/ | core.views.start_design | templates/core/onboarding_step1.html | 
/<lang>/websites/ | core.views.websites | templates/core/blog_index.html | 
/<lang>/products/ | core.views.products_index | templates/core/product_page.html | 
/<lang>/products/websites/ | core.views.product_websites | templates/core/product_page.html | 
/<lang>/products/seo/ | core.views.product_seo | templates/core/product_page.html | 
/<lang>/products/print-studio/ | core.views.product_print_studio | templates/core/product_page.html | 
/<lang>/products/pos-systems/ | core.views.product_pos_systems | templates/core/product_page.html | 
/<lang>/products/ads/ | core.views.product_ads | templates/core/product_page.html | 
/<lang>/products/uptime-status/ | core.views.product_uptime_status | templates/core/product_page.html | 
/<lang>/products/support/ | core.views.product_support | templates/core/product_page.html | 
/<lang>/products/maintenance/ | core.views.product_maintenance | templates/core/product_page.html | 
/<lang>/products/ecommerce/ | core.views.product_ecommerce | templates/core/product_page.html | 
/<lang>/websites/one-page/ | core.views.websites_one_page | templates/core/websites_one_page_plan.html | 
/<lang>/websites/multi-page/ | core.views.websites_multi_page | templates/pages/websites/multi_page_plan.html | 
/<lang>/websites/multi-page-seo/ | core.views.websites_multi_page_seo | templates/pages/websites/multi_page_seo_plan.html | 
/<lang>/websites/catalog-site/ | core.views.websites_catalog_site | templates/pages/websites/catalog_site_plan.html | 
/<lang>/websites/eshop-starter/ | core.views.websites_eshop_starter | templates/pages/websites/starter_estore_plan.html | 
/<lang>/websites/starter-estore/ | core.views.websites_eshop_starter | templates/pages/websites/starter_estore_plan.html | 
/<lang>/websites/eshop-premium/ | core.views.websites_eshop_premium | templates/pages/websites/premium_estore_plan.html | 
/<lang>/websites/custom/ | core.views.websites_custom | templates/pages/websites/custom_website_plan.html | 
/<lang>/websites/custom-website/ | core.views.websites_custom | templates/pages/websites/custom_website_plan.html | 
/<lang>/services/ | core.views.services | templates/core/services.html | 
/<lang>/pos-systems/ | core.views.pos_systems | templates/core/pos_systems.html | 
/<lang>/pos-systems/retail/ | core.views.pos_systems_retail | templates/core/pos_systems.html | 
/<lang>/pos-systems/hospitality/ | core.views.pos_systems_hospitality | templates/core/pos_systems.html | 
/<lang>/pos-systems/services/ | core.views.pos_systems_services | templates/core/pos_systems.html | 
/<lang>/pos-systems/compare/ | core.views.pos_systems_compare | templates/core/pos_systems.html | 
/<lang>/pos-systems/faq/ | core.views.pos_systems_faq | templates/core/pos_systems.html | 
/<lang>/help-center/ | core.views.help_center | templates/core/help_center.html | 
/<lang>/blog/ | core.views.blog_index | templates/core/print_lab.html | 
/<lang>/blog/<slug:slug>/ | core.views.blog_detail | templates/core/blog_detail.html | 
/<lang>/printlab/ | core.views.printlab | templates/core/product_page.html | 
/<lang>/printlab/start/ | core.views.printlab_start | templates/redirect | 
/<lang>/printlab/business-cards/ | core.views.printlab_business_cards | templates/core/product_page.html | 
/<lang>/printlab/flyers/ | core.views.printlab_flyers | templates/core/product_page.html | 
/<lang>/printlab/brochures/ | core.views.printlab_brochures | templates/core/product_page.html | 
/<lang>/printlab/stickers/ | core.views.printlab_stickers | templates/core/product_page.html | 
/<lang>/printlab/apparel/ | core.views.printlab_apparel | templates/core/product_page.html | 
/<lang>/printlab/merch/ | core.views.printlab_merch | templates/core/product_page.html | 
/<lang>/billing/ | core.views.billing | templates/core/billing.html | 
/<lang>/billing/checkout/ | core.views.billing_checkout | templates/core/billing_checkout.html | 
/<lang>/billing/success/ | core.views.billing_success | templates/core/billing_success.html | 
/<lang>/billing/cancel/ | core.views.billing_cancel | templates/core/billing_cancel.html | 
/<lang>/billing/portal/ | core.views.billing_portal | templates/core/billing_portal.html | 
/<lang>/printful/ | core.views.printful | templates/core/printful.html | 
/<lang>/printful/products/ | core.views.printful_products | templates/core/printful_products.html | 
/<lang>/printful/orders/ | core.views.printful_orders | templates/core/printful_orders.html | 
/<lang>/locations/<str:country>/ | core.views.location_country | templates/redirect | 
/<lang>/locations/<str:country>/<slug:city>/ | core.views.location_city | templates/site/404.html | 
/<lang>/<slug:slug>/ | core.views.public_page | templates/site/page.html | 
/<lang>/print-lab/ | core.views.RedirectView | templates/redirect | redirect -> core:printlab
/<lang>/print-lab/products/ | core.views.RedirectView | templates/redirect | redirect -> core:printlab
/<lang>/print-lab/how-it-works/ | core.views.RedirectView | templates/redirect | redirect -> core:printlab
/<lang>/print-lab/faq/ | core.views.RedirectView | templates/redirect | redirect -> core:printlab

## Per-Page Section Map
### templates/core/billing.html

### templates/core/billing_cancel.html

### templates/core/billing_checkout.html

### templates/core/billing_portal.html

### templates/core/billing_success.html

### templates/core/blog_detail.html

### templates/core/blog_index.html

### templates/core/help_center.html

### templates/core/onboarding_step1.html

### templates/core/pos_systems.html

### templates/core/print_lab.html

### templates/core/printful.html

### templates/core/printful_orders.html

### templates/core/printful_products.html

### templates/core/product_page.html

### templates/core/services.html

### templates/core/websites_one_page_plan.html

### templates/pages/websites/catalog_site_plan.html

### templates/pages/websites/custom_website_plan.html

### templates/pages/websites/multi_page_plan.html

### templates/pages/websites/multi_page_seo_plan.html

### templates/pages/websites/premium_estore_plan.html

### templates/pages/websites/starter_estore_plan.html

### templates/site/404.html
- extends: site/base.html

### templates/site/page.html
- extends: site/base.html

## Orphan/Unused Templates & Partials
- templates/components/blog_latest_slider.html
- templates/components/upgrade_cta.html
- templates/controlpanel/billing.html
- templates/controlpanel/content_map.html
- templates/controlpanel/dashboard.html
- templates/controlpanel/domains_hosting.html
- templates/controlpanel/home.html
- templates/controlpanel/plans_form.html
- templates/controlpanel/plans_list.html
- templates/controlpanel/templates.html
- templates/controlpanel/templates_form.html
- templates/controlpanel/templates_list.html
- templates/controlpanel/tenant_edit.html
- templates/controlpanel/tenants.html
- templates/controlpanel/users.html
- templates/core/dashboard.html
- templates/core/footer.html
- templates/core/home_db.html
- templates/core/main_nav.html
- templates/core/pos_systems_compare.html
- templates/core/pos_systems_hospitality.html
- templates/core/pos_systems_retail.html
- templates/core/right_sidebar.html
- templates/ops/home.html
- templates/ops/site_detail.html
- templates/ops/sites_list.html
- templates/registration/login.html
- templates/site/home.html
- templates/site/location_landing.html
- templates/site/sections/contact.html
- templates/site/sections/cta.html
- templates/site/sections/faq.html
- templates/site/sections/features.html
- templates/site/sections/hero.html
- templates/site/sections/location.html
- templates/site/sections/pricing.html
- templates/site/sections/printlab.html
- templates/site/sections/services.html
- templates/site/sections/unknown.html

## Placeholder / Risky Copy Findings
- templates/components/blog_latest_slider.html:88 [placeholder] <img class="jcw-blog-card-image" src="{% static 'jcw/placeholders/blog/blog-1.svg' %}" alt="{{ post.localized_title }}">
- templates/components/blog_latest_slider.html:90 [placeholder] <img class="jcw-blog-card-image" src="{% static 'jcw/placeholders/blog/blog-2.svg' %}" alt="{{ post.localized_title }}">
- templates/components/blog_latest_slider.html:92 [placeholder] <img class="jcw-blog-card-image" src="{% static 'jcw/placeholders/blog/blog-3.svg' %}" alt="{{ post.localized_title }}">
- templates/components/blog_latest_slider.html:94 [placeholder] <img class="jcw-blog-card-image" src="{% static 'jcw/placeholders/blog/blog-4.svg' %}" alt="{{ post.localized_title }}">
- templates/components/blog_latest_slider.html:96 [placeholder] <img class="jcw-blog-card-image" src="{% static 'jcw/placeholders/blog/blog-1.svg' %}" alt="{{ post.localized_title }}">
- templates/core/blog_index.html:76 [placeholder] <img class="w-full h-48 object-cover" src="{% static 'jcw/placeholders/blog/blog-1.svg' %}" alt="{{ post.localized_title }}">
- templates/core/blog_index.html:78 [placeholder] <img class="w-full h-48 object-cover" src="{% static 'jcw/placeholders/blog/blog-2.svg' %}" alt="{{ post.localized_title }}">
- templates/core/blog_index.html:80 [placeholder] <img class="w-full h-48 object-cover" src="{% static 'jcw/placeholders/blog/blog-3.svg' %}" alt="{{ post.localized_title }}">
- templates/core/blog_index.html:82 [placeholder] <img class="w-full h-48 object-cover" src="{% static 'jcw/placeholders/blog/blog-4.svg' %}" alt="{{ post.localized_title }}">
- templates/core/blog_index.html:84 [placeholder] <img class="w-full h-48 object-cover" src="{% static 'jcw/placeholders/blog/blog-1.svg' %}" alt="{{ post.localized_title }}">
- templates/core/footer.html:201 [placeholder] <input type="email" placeholder="{% trans 'Enter your email' %}" class="px-3 py-1 rounded-l-md bg-blue-800 text-white text-sm border-0 focus:ring-1 focus:ring-white outline-none">
- templates/core/help_center.html:187 [placeholder] <input type="text" placeholder="Search for help articles..." class="w-full px-4 py-3 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
- templates/core/home.html:1837 [placeholder] 'label":"Basic reports","title":"See what is selling","description":"Get simple overviews of turnover, payment methods and busy days without a full accounting system.","highlight":"Clear and easy to read"}\n26:["$27","$28","$29"]\n2b:{"label":"Website copy assistant","title":"Texts for your pages in your tone","description":"Generate headlines, service descriptions and about pages using your business details and preferred style.","highlight":"Based on your answers"}\n2c:{"label":"Blog \u0026 update generator","title":"Keep your site active","description":"Create posts with ideas, structure and draft texts you can quickly review and publish.","highlight":"Good for Google \u0026 clients"}\n2d:{"label":"Screenshot-to-layout helper","title":"Turn ideas into layouts","description":"Use example screenshots as inspiration and turn them into layouts that fit your own brand.","highlight":"Saves design time"}\n2a:["$2b","$2c","$2d"]\n21:{"solutionsTitle":"Choose Your Perfect Solution","printingTitle":"Your brand, beautifully printed.","printingText":"Placeholder section ? we\'ll later add the full printing layout from your old homepage.","posTitle":"Modern POS systems that grow with you.","posText":"Placeholder for POS systems content.","aiTitle":"MagicAI tools.","aiText":"Placeholder for AI tool cards: content writer, blog generator, screenshot-to-site, etc.","pricingTitle":"Pricing overview.","pricingText":"Placeholder ? later we match your real pricing tables.","printingCards":"$22","posCards":"$26","aiCards":"$2a"}\n2f:{"title":"Services","websites":"Website Design","pos":"Card Payments","printing":"Print Design","consulting":"Business Consulting","maintenance":"Website Maintenance","hosting":"Web Hosting"}\n30:{"title":"Company","about":"About Us","team":"Our Team","careers":"Careers","news":"News \u0026 Updates","partners":"Partners","testimonials":"Testimonials"}\n31:{"title":"Tools","jsonReader":"JSON Reader","qrGenerator":"QR Generator","passwordChecker":"Password Checker","passwordGenerator":"Password Generator","imageResizer":"Image Re',
- templates/core/home.html:1843 [placeholder] 'sizer","imageCropper":"Image Cropper"}\n32:{"title":"Support","help":"Help Center","contact":"Contact Us","faq":"FAQ","documentation":"Documentation","tutorials":"Video Tutorials","community":"Community Forum"}\n33:{"privacy":"Privacy Policy","terms":"Terms of Service","cookies":"Cookie Policy","gdpr":"GDPR Compliance"}\n34:{"title":"Subscribe to our newsletter","placeholder":"Enter your email","subscribe":"Subscribe"}\n35:{"rights":"All rights reserved.","made":"Made with","location":"in Portugal","powered":"Powered by"}\n2e:{"tagline":"Websites ? Printing ? POS ? Tools","description":"We help small EU businesses get online with modern websites, matching print materials, and simple tools ? all connected in one system.","services":"$2f","company":"$30","tools":"$31","support":"$32","legal":"$33","newsletter":"$34","copyright":"$35"}\n37:{"step1Label":"Business details","step2Label":"Services \u0026 website type","step3Label":"Colours \u0026 style","step4Label":"Review","next":"Next","previous":"Back","finish":"Finish and review"}\n38:{"businessName":"Business name","country":"Country","city":"City","contactEmail":"Contact email","contactPhone":"Phone / WhatsApp","websiteType":"Type of website","onePage":"One-page website","multiPage":"Multi-page website","store":"Online store","servicesLabel":"Main services","servicesHint":"List a few services, separated by commas.","colorsLabel":"Preferred colours","colorsHint":"For example: blue and white, or your existing brand colours.","styleLabel":"Style","styleHint":"Example: modern and clean, warm and friendly, luxury, etc."}\n39:{"title":"Review your setup","description":"Check if these details look correct. In the next step we\'ll generate your website draft based on this information.","businessSection":"Business details","servicesSection":"Services \u0026 website type","styleSection":"Colours \u0026 style","changeNote":"You can still change all of this later in your dashboard before publishing."}\n36:{"title":"Website builder","subtitle":"Answer a few simple questions and we\'ll prepare your',
- templates/core/home.html:1849 [placeholder] ' website, printing and basic POS setup for you.","introBadge":"Step 1 of 4","introTitle":"Let\'s start with the basics.","introText":"We\'ll ask about your business, services and preferred colours. You can always change everything later.","startButton":"Start the wizard","backHome":"Back to homepage","steps":"$37","fields":"$38","review":"$39"}\n3d:["Up to 6 services on a single page","Contact / WhatsApp / call buttons","Mobile-optimised design","Basic SEO structure for Google"]\n3c:{"id":"one-page","name":"One-page website","short":"For simple local businesses","price":"From ?X / month","bestFor":"Ideal if you have a few services and just need a ","features":"$3d","highlight":"Great starter option"}\n3f:["Service pages that can rank on Google","Blog or news section","Portfolio / projects pages","More space for photos and explanations"]\n3e:{"id":"multi-page","name":"Multi-page website","short":"For growing businesses","price":"From ?Y / month","bestFor":"Good if you want separate pages for services, ","features":"$3f","highlight":"Most flexible choice"}\n41:["Product catalogue and categories","Simple checkout and payment options","Order notifications","Basic sales overview"]\n40:{"id":"store","name":"Online store","short":"For selling products online","price":"From ?Z / month","bestFor":"For businesses that want to accept orders and payments directly through the website.","features":"$41","highlight":"Best if you sell products"}\n3b:["$3c","$3e","$40"]\n3a:{"title":"Simple pricing that grows with you.","subtitle":"Start small and upgrade later. All plans include hosting, security updates and basic support.","note":"Real prices will be confirmed later ? these are placeholders.","plans":"$3b"}\n44:{"id":"local-service-01","name":"Local service (clean \u0026 simple)","type":"One-page layout","bestFor":"Ideal for handymen, cleaners, coaches, tutors, small local services.","complexity":"Fast to launch","highlight":"Recommended for simple service businesses."}\n45:{"id":"mul',
- templates/core/home.html:1873 [placeholder] '0","websites":"$52","services":"$54","helpCenter":"$56","common":"$59"}\n5c:{"intent":"Intent","details":"Details","branding":"Branding"}\n5e:{"title":"Build a Website","description":"Create a professional website for your business"}\n5f:{"title":"Design Prints","description":"Create business cards, flyers, and marketing materials"}\n60:{"title":"Point of Sale","description":"Set up payment processing and inventory management"}\n5d:{"website":"$5e","prints":"$5f","pos":"$60"}\n62:{"label":"Business Name","placeholder":"Enter your business name","required":"Business name is required"}\n63:{"label":"Business Type","placeholder":"e.g., Restaurant, Consulting, Retail Store"}\n64:{"label":"Primary Country","placeholder":"Select your country"}\n65:{"label":"Primary Language","placeholder":"Select primary language"}\n66:{"label":"Primary Goal","placeholder":"What\'s your main goal?"}\n67:{"primaryLabel":"Primary Brand Color","secondaryLabel":"Secondary Brand Color","primaryPlaceholder":"#1D4ED8","secondaryPlaceholder":"#6366F1"}\n68:{"label":"Preferred Theme","light":"Light","dark":"Dark","auto":"Auto"}\n69:{"label":"Additional Notes","placeholder":"Any specific requirements or preferences..."}\n61:{"businessName":"$62","businessType":"$63","primaryCountry":"$64","primaryLanguage":"$65","primaryGoal":"$66","brandColors":"$67","themeMode":"$68","notes":"$69"}\n6a:{"back":"Back","continue":"Continue to Branding","continueDetails":"Continue to Details","complete":"Complete Setup","creating":"Creating..."}\n6b:{"title":"Welcome to JustCodeWorks!","subtitle":"Your onboarding is complete. Redirecting to your dashboard...","redirecting":"Redirecting..."}\n6c:{"general":"Something went wrong. Please try again.","businessName":"Business name cannot be empty","invalidColor":"Please enter a valid hex color (e.g. #1D4ED8)","submitFailed":"Failed to save onboarding data. Please try again."}\n6d:["United States","United Kingdom","Canada","Australia","Germany","France","Spain","Portugal","Brazil","Mexico","Other"]\n6e:{"en":"English","pt":"Portugu?s","e',
- templates/core/home.html:1885 [placeholder] '4:[["$","$L14",null,{"locale":"en"}],["$","$L15",null,{"locale":"en","dict":{"hero":{"badge":"Everything connected: website, printing \u0026 AI.","title":"Everything you need to get your business online.","subtitle":"Launch a modern website, order your print materials, connect simple POS tools and let your AI assistant do the heavy lifting ? all from one place.","ctaPrimary":"Start in 2 minutes","ctaSecondary":"View demo website","note":"No tech skills needed. Perfect for small businesses, freelancers and local shops.","previewDomain":"grandmas-cookies.justcodeworks.eu","previewTitle":"Grandma\'s Cookie Shop","previewText":"Fresh cookies baked daily. Order online or visit our cozy shop.","previewWebsiteLabel":"Website","previewWebsiteText":"Online in 1?2 days","previewPrintLabel":"Printing","previewPrintText":"Cards \u0026 flyers","previewAiLabel":"MagicAI","previewAiText":"Texts \u0026 images","assistantTitle":"Clippy 2.0 is ready","assistantText":"\\"Answer a few questions and I\'ll build everything for you.\\"","assistantCta":"Start wizard"},"nav":{"home":"Home","websites":"Websites","printing":"Printing","pos":"Card Payments","services":"Services","helpCenter":"Help Center","aiTools":"MagicAI Tools","pricing":"Pricing","login":"Login","start":"Start building","templates":"Templates"},"websites":{"title":"Websites that work as hard as you do","subtitle":"Choose the type of website that fits your business today ? and upgrade later as you grow.","badge":"Website Builder","onePage":{"badge":"One-page websites","title":"Perfect for simple local businesses","desc":"Simple, focused site for a few services. Easy to launch and easy to update. ","bullets":["Up to 6 services on one page","Contact / WhatsApp / call buttons","Optimised for mobile visitors"],"priceLabel":"From ?X / month","link":"View example"},"multiPage":{"badge":"Multi-page websites","title":"Grow with dedicated pages for each service","desc":"Add pages for services, projects, team, and FAQs without rebuilding your site. ","bullets":["Service pages that can rank on Google","Blog / news sections for updates","Structured contact \u0026 quote forms"],"priceLabel":"From ?Y / month","link":"View example"},"ecommerce":{"badge":"Online stores","title":"Sell your products with a simple store","desc":"Sell products or bookings with a simple store, and upgrade as your catalog grows. ","bullets":["Product catalogue and categories","Simple checkout and payment options","Order notifications and basic reports"],"priceLabel":"From ?Z / month","link":"View example"}},"sections":{"solutionsTitle":"Choose Your Perfect Solution","printingTitle":"Your brand, beautifully printed.","printingText":"Placeholder section ? we\'ll later add the full printing layout from your old homepage.","posTitle":"Modern POS systems that grow with you.","posText":"Placeholder for POS systems content.","aiTitle":"MagicAI tools.","aiText":"Placeholder for AI tool cards: content writer, blog generator, screenshot-to-site, etc.","pricingTitle":"Pricing overview.","pricingText":"Placeholder ? later we match your real pricing tables.","printingCards":[{"label":"Business cards","title":"Make a strong first impression","description":"Classic or modern designs with your logo, colours and contact details, ready to hand out to new customers.","highlight":"Most popular starter item"},{"label":"Flyers \u0026 brochures","title":"Promote your services locally","description":"Perfect for door-to-door drops, local shops and events. Great for construction, beauty, coaching and more.","highlight":"Ideal for local marketing"},{"label":"Stickers, labels \u0026 merch","title":"Put your brand everywhere","description":"Brand your packaging, gifts and products with stickers, labels and simple merch items.","highlight":"Add-on for growing brands"}],"posCards":[{"label":"Simple card terminals","title":"Take payments without headaches","description":"Connect a simple terminal that just works: tap, pin, receipt. No complex systems needed.","highlight":"Great for small shops"},{"label":"Tablet \u0026 phone POS","title":"Use the devices you already own","description":"Turn a tablet or phone into a small POS for services, salons, caf?s and pop-up businesses.","highlight":"Flexible for mobile work"},{"label":"Basic reports","title":"See what is selling","description":"Get simple overviews of turnover, payment methods and busy days without a full accounting system.","highlight":"Clear and easy to read"}],"aiCards":[{"label":"Website copy assistant","title":"Texts for your pages in your tone","description":"Generate headlines, service descriptions and about pages using your business details and preferred style.","highlight":"Based on your answers"},{"label":"Blog \u0026 update generator","title":"Keep your site active","description":"Create posts with ideas, structure and draft texts you can quickly review and publish.","highlight":"Good for Google \u0026 clients"},{"label":"Screenshot-to-layout helper","title":"Turn ideas into layouts","description":"Use example screenshots as inspiration and turn them into layouts that fit your own brand.","highlight":"Saves design time"}]},"footer":{"tagline":"Websites ? Printing ? POS ? Tools","description":"We help small EU businesses get online with modern websites, matching print materials, and simple tools ? all connected in one system.","services":{"title":"Services","websites":"Website Design","pos":"Card Payments","printing":"Print Design","consulting":"Business Consulting","maintenance":"Website Maintenance","hosting":"Web Hosting"},"company":{"title":"Company","about":"About Us","team":"Our Team","careers":"Careers","news":"News \u0026 Updates","partners":"Partners","testimonials":"Testimonials"},"tools":{"title":"Tools","jsonReader":"JSON Reader","qrGenerator":"QR Generator","passwordChecker":"Password Checker","passwordGenerator":"Password Generator","imageResizer":"Image Resizer","imageCropper":"Image Cropper"},"support":{"title":"Support","help":"Help Center","contact":"Contact Us","faq":"FAQ","documentation":"Documentation","tutorials":"Video Tutorials","community":"Community Forum"},"legal":{"privacy":"Privacy Policy","terms":"Terms of Service","cookies":"Cookie Policy","gdpr":"GDPR Compliance"},"newsletter":{"title":"Subscribe to our newsletter","placeholder":"Enter your email","subscribe":"Subscribe"},"copyright":{"rights":"All rights reserved.","made":"Made with","location":"in Portugal","powered":"Powered by"}},"builder":{"title":"Website builder","subtitle":"Answer a few simple questions and we\'ll prepare your website, printing and basic POS setup for you.","introBadge":"Step 1 of 4","introTitle":"Let\'s start with the basics.","introText":"We\'ll ask about your business, services and preferred colours. You can always change everything later.","startButton":"Start the wizard","backHome":"Back to homepage","steps":{"step1Label":"Business details","step2Label":"Services \u0026 website type","step3Label":"Colours \u0026 style","step4Label":"Review","next":"Next","previous":"Back","finish":"Finish and review"},"fields":{"businessName":"Business name","country":"Country","city":"City","contactEmail":"Contact email","contactPhone":"Phone / WhatsApp","websiteType":"Type of website","onePage":"One-page website","multiPage":"Multi-page website","store":"Online store","servicesLabel":"Main services","servicesHint":"List a few services, separated by commas.","colorsLabel":"Preferred colours","colorsHint":"For example: blue and white, or your existing brand colours.","styleLabel":"Style","styleHint":"Example: modern and clean, warm and friendly, luxury, etc."},"review":{"title":"Review your setup","description":"Check if these details look correct. In the next step we\'ll generate your website draft based on this information.","businessSection":"Business details","servicesSection":"Services \u0026 website type","styleSection":"Colours \u0026 style","changeNote":"You can still change all of this later in your dashboard before publishing."}},"pricing":{"title":"Simple pricing that grows with you.","subtitle":"Start small and upgrade later. All plans include hosting, security updates and basic support.","note":"Real prices will be confirmed later ? these are placeholders.","plans":[{"id":"one-page","name":"One-page website","short":"For simple local businesses","price":"From ?X / month","bestFor":"Ideal if you have a few services and just need a ","features":["Up to 6 services on a single page","Contact / WhatsApp / call buttons","Mobile-optimised design","Basic SEO structure for Google"],"highlight":"Great starter option"},{"id":"multi-page","name":"Multi-page website","short":"For growing businesses","price":"From ?Y / month","bestFor":"Good if you want separate pages for services, ","features":["Service pages that can rank on Google","Blog or news section","Portfolio / projects pages","More space for photos and explanations"],"highlight":"Most flexible choice"},{"id":"store","name":"Online store","short":"For selling products online","price":"From ?Z / month","bestFor":"For businesses that want to accept orders and payments directly through the website.","features":["Product catalogue and categories","Simple checkout and payment options","Order notifications","Basic sales overview"],"highlight":"Best if you sell products"}]},"templates":{"title":"Choose a starting point for your website.","subtitle":"Pick a layout that fits your type of business. We\'ll adapt colours, photos and texts to your details.","badge":"Step 1 ? Choose a template","note":"These are example layouts. You can change everything later.","list":[{"id":"local-service-01","name":"Local service (clean \u0026 simple)","type":"One-page layout","bestFor":"Ideal for handymen, cleaners, coaches, tutors, small local services.","complexity":"Fast to launch","highlight":"Recommended for simple service businesses."},{"id":"multi-service-01","name":"Multi-service company","type":"Multi-page layout","bestFor":"Good for construction, renovation, beauty salons and other businesses with several services.","complexity":"More space for content","highlight":"Best when you have multiple main services."},{"id":"store-01","name":"Simple online store","type":"Store layout","bestFor":"For small shops that want to show products and accept basic online orders.","complexity":"Includes product grid","highlight":"Good starting point for small ecommerce."}],"buttons":{"useTemplate":"Use this template","backHome":"Back to homepage","goToBuilder":"Continue to builder"}},"auth":{"login":{"title":"Login to your Just Code Works account","subtitle":"Access your websites, drafts, print orders and MagicAI tools from your dashboard.","emailLabel":"Email","passwordLabel":"Password","button":"Login","noAccount":"Don\'t have an account yet?","goToRegister":"Create an account","backHome":"Back to homepage","note":"This is a demo login page. In the full version, this will connect to the real authentication system."},"register":{"title":"Create your Just Code Works account","subtitle":"We\'ll use these details to connect your websites, print orders and billing in one place.","nameLabel":"Name","emailLabel":"Email","passwordLabel":"Password","button":"Create account","haveAccount":"Already have an account?","goToLogin":"Go to login","backHome":"Back to homepage","note":"This is a demo registration page. In the full version, this will create a real account for you."}},"reviewPage":{"title":"Your setup summary","subtitle":"Here\'s what we\'ll use to generate your website draft and suggest print items.","missingDataTitle":"No data found yet","missingDataText":"It looks like you haven\'t completed the builder wizard yet. Please go through the steps first.","backToBuilder":"Go back to builder","backHome":"Back to homepage","selectedTemplate":"Selected template","builderDataTitle":"Information from the builder","businessSection":"Business details","servicesSection":"Services \u0026 website type","styleSection":"Colours \u0026 style","editInBuilder":"Change in builder"},"pages":{"home":{"title":"Just Code Works - Home","subtitle":"Welcome to our homepage","pageInfo":"Page Info","languageTesting":"Language Testing","languageHelp":"Use the selector above to test different language versions of the site.","navigation":"Navigation","published":"Published","systemOverview":{"title":"? System Overview","template":"Template","templateName":"jcw-main","sections":"Sections","sectionsList":"Hero, Features, Services, Solutions, Contact","status":"Status","statusActive":"? Active \u0026 Ready","description":"Just Code Works provides comprehensive business solutions that adapt to your needs."},"multiLanguageSupport":{"title":"? Multi-Language Support","description":"Our platform supports 6 languages with automatic content translation and localized routing.","languages":"Languages: English, Dutch, Portuguese, Spanish, French, German","testInstructions":"Use the language selector to experience seamless multi-language navigation."}},"posystems":{"title":"Card Payments","subtitle":"Modern point-of-sale solutions for your business","features":{"payment":"Payment Processing","paymentDesc":"Accept credit, debit, and contactless payments with competitive rates and fast processing.","inventory":"Inventory Management","inventoryDesc":"Track stock, set low stock alerts, and manage products with ease through our intuitive interface.","analytics":"Sales Analytics","analyticsDesc":"Get insights on sales patterns, top-selling products, and financial performance with detailed reports."}},"websites":{"title":"Websites","subtitle":"Custom websites and web development services","features":{"onePage":"One-Page Sites","onePageDesc":"Perfect for small businesses and portfolios. Get online quickly with a modern, responsive design.","multiPage":"Multi-Page Websites","multiPageDesc":"Complete business websites with multiple pages, navigation, and custom functionality.","ecommerce":"Online Shops","ecommerceDesc":"E-commerce websites with shopping carts, payment processing, and inventory management."}},"services":{"title":"Services","subtitle":"All our professional services","features":{"webDev":"Web Development","webDevDesc":"Custom websites and web applications built with modern technologies.","mobileApps":"Mobile Apps","mobileAppsDesc":"Native and cross-platform mobile applications for iOS and Android.","cloud":"Cloud Solutions","cloudDesc":"Scalable cloud infrastructure and deployment solutions for your applications.","maintenance":"Maintenance","maintenanceDesc":"Ongoing support and maintenance for your existing digital solutions."}},"helpCenter":{"title":"Help Center","subtitle":"Get help and support","features":{"documentation":"Documentation","documentationDesc":"Complete guides and documentation for all our products and services.","support":"Support","supportDesc":"Get direct help from our technical support team for any questions or issues.","faq":"FAQ","faqDesc":"Find answers to the most frequently asked questions about our services.","tutorials":"Tutorials","tutorialsDesc":"Step-by-step tutorials and video guides to help you get the most out of our platform.","categories":{"getting":"Getting Started Guides","api":"API Documentation","practices":"Best Practices","live":"Live Chat Support","email":"Email Support","phone":"Phone Support","billing":"Billing Questions","technical":"Technical Issues","account":"Account Management","video":"Video Tutorials","written":"Written Guides","interactive":"Interactive Examples"}}},"common":{"title":"Title","slug":"Slug","path":"Path","language":"Language","order":"Order","project":"Project","template":"Template","loading":"Loading..."}},"onboarding":{"step0":{"title":"Let\'s Get Started","subtitle":"Tell us about your business and what you\'d like to create","progress":{"intent":"Intent","details":"Details","branding":"Branding"},"intents":{"website":{"title":"Build a Website","description":"Create a professional website for your business"},"prints":{"title":"Design Prints","description":"Create business cards, flyers, and marketing materials"},"pos":{"title":"Point of Sale","description":"Set up payment processing and inventory management"}},"form":{"businessName":{"label":"Business Name","placeholder":"Enter your business name","required":"Business name is required"},"businessType":{"label":"Business Type","placeholder":"e.g., Restaurant, Consulting, Retail Store"},"primaryCountry":{"label":"Primary Country","placeholder":"Select your country"},"primaryLanguage":{"label":"Primary Language","placeholder":"Select primary language"},"primaryGoal":{"label":"Primary Goal","placeholder":"What\'s your main goal?"},"brandColors":{"primaryLabel":"Primary Brand Color","secondaryLabel":"Secondary Brand Color","primaryPlaceholder":"#1D4ED8","secondaryPlaceholder":"#6366F1"},"themeMode":{"label":"Preferred Theme","light":"Light","dark":"Dark","auto":"Auto"},"notes":{"label":"Additional Notes","placeholder":"Any specific requirements or preferences..."}},"actions":{"back":"Back","continue":"Continue to Branding","continueDetails":"Continue to Details","complete":"Complete Setup","creating":"Creating..."},"success":{"title":"Welcome to JustCodeWorks!","subtitle":"Your onboarding is complete. Redirecting to your dashboard...","redirecting":"Redirecting..."},"errors":{"general":"Something went wrong. Please try again.","businessName":"Business name cannot be empty","invalidColor":"Please enter a valid hex color (e.g. #1D4ED8)","submitFailed":"Failed to save onboarding data. Please try again."},"countries":["United States","United Kingdom","Canada","Australia","Germany","France","Spain","Portugal","Brazil","Mexico","Other"],"languages":{"en":"English","pt":"Portugu?s","es":"Espa?ol","fr":"Fran?ais","de":"Deutsch"},"goals":{"get-leads":"Get leads / requests","show-info":"Show info / menu","sell-online":"Sell online","take-bookings":"Take bookings","other":"Other"}}},"websitePromise":{"items":["Free domain and hosting first year","Secure EU-based servers","SSL certificate and daily backups","Fast delivery time","Ongoing upgrade options"],"description":"All websites are built with our smart system that makes content creation simple and intuitive ? so you can focus on your business, not the tools.","exploreTitle":"Explore Our Website Types"}}}],["$","$L16",null,{"dict":"$17"}]]\n',
- templates/core/onboarding_step1.html:44 [placeholder] <input id="country" name="country" type="text" value="{{ draft.country }}" class="w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="{% trans 'e.g. PT' %}">
- templates/core/printful.html:49 [Printful] <li><a class="underline" href="{% url 'core:printful_products' %}">Products</a></li>
- templates/core/printful.html:50 [Printful] <li><a class="underline" href="{% url 'core:printful_orders' %}">Orders</a></li>
- templates/core/printful.html:51 [Printful] <li><a class="underline" href="/en/printful/settings/">Settings</a></li>
- templates/core/print_lab_faq.html:96 [Printful] {% if sections_by_key.printful_policy_notice %}
- templates/core/print_lab_faq.html:98 [Printful] <h3 class="jsx-e826c9b2f8ec5a67 text-xl font-bold text-slate-900 dark:text-white mb-2">{{ sections_by_key.printful_policy_notice.content.heading }}</h3>
- templates/core/print_lab_faq.html:99 [Printful] <p class="jsx-e826c9b2f8ec5a67 text-sm text-slate-600 dark:text-slate-300">{{ sections_by_key.printful_policy_notice.content.body }}</p>
- templates/core/print_lab_faq.html:100 [Printful] {% if sections_by_key.printful_policy_notice.content.cta_primary_url %}
- templates/core/print_lab_faq.html:101 [Printful] <a href="{{ sections_by_key.printful_policy_notice.content.cta_primary_url }}" class="jsx-e826c9b2f8ec5a67 mt-3 inline-block text-sm font-semibold text-blue-700 hover:underline" target="_blank" rel="noopener">{{ sections_by_key.printful_policy_notice.content.cta_primary_text }}</a>
- templates/core/sections/printlab_paper_products.html:7 [placeholder] src="{% static 'jcw/placeholders/blog/blog-1.svg' %}"
- templates/dashboard/blog.html:11 [placeholder] <input class="dashboard-input" type="text" placeholder="{% trans 'Search posts' %}" disabled>
- templates/dashboard/marketplace_card_payments.html:14 [placeholder] {% trans "This section is a placeholder and will be expanded soon." %}
- templates/dashboard/marketplace_jcw.html:14 [placeholder] {% trans "This section is a placeholder and will be expanded soon." %}
- templates/dashboard/marketplace_printlab.html:14 [placeholder] {% trans "This section is a placeholder and will be expanded soon." %}
- templates/dashboard/pages.html:23 [placeholder] <input class="dashboard-input" type="text" placeholder="{% trans 'Search pages' %}" {% if not feature_flags.can_use_custom_pages %}disabled{% endif %}>
- templates/dashboard/print_studio.html:38 [Printful] <span class="dashboard-badge">{% trans "Printful" %}</span>
- templates/dashboard/print_studio.html:58 [Printful] <span>{% trans "Printful" %}</span>
- templates/dashboard/print_studio.html:14 [Bizay] <span class="dashboard-badge">{% trans "Bizay soon" %}</span>
- templates/dashboard/print_studio.html:22 [Bizay] <span class="dashboard-badge">{% trans "Bizay soon" %}</span>
- templates/dashboard/print_studio.html:30 [Bizay] <span class="dashboard-badge">{% trans "Bizay soon" %}</span>
- templates/dashboard/print_studio.html:62 [Bizay] <span>{% trans "Bizay" %}</span>
- templates/dashboard/visibility.html:52 [placeholder] <input id="visibility-country" class="dashboard-input" type="text" disabled placeholder="{% trans 'Select countries' %}">
- templates/dashboard/visibility.html:56 [placeholder] <input id="visibility-city" class="dashboard-input" type="text" disabled placeholder="{% trans 'Select cities' %}">
- templates/pages/websites/custom_website_plan.html:219 [placeholder] <div class="text-sm text-slate-500 mb-4">{% trans "Preview placeholder" %}</div>
- templates/pages/websites/multi_page_plan.html:143 [Printful] <span class="px-3 py-1 rounded-full bg-slate-100">{% trans "Printful" %}</span>
- templates/pages/websites/multi_page_seo_plan.html:122 [Printful] <span class="px-3 py-1 rounded-full bg-slate-100">{% trans "Printful" %}</span>
- templates/pages/websites/premium_estore_plan.html:210 [Printful] <span class="px-3 py-1 rounded-full bg-white">{% trans "Printful" %}</span>

## "We" Wording Findings
- templates/core/footer.html:11 {% trans "We help small EU businesses get online with modern websites, matching print materials, and simple tools - all connected in one system." %}
- templates/core/home.html:1338 {% trans "We help you choose a reliable POS that fits your business. Simple, clear, and practical." %}
- templates/core/onboarding_step1.html:24 <p class="text-slate-600 mb-8">{% trans "We will use this to personalize your draft site." %}</p>
- templates/core/printlab_start.html:15 {% trans "Designer coming soon. We're preparing this category for you now." %}
- templates/core/product_page.html:119 <p class="text-sm text-gray-600">{% trans "We check and confirm your order." %}</p>
- templates/core/product_page.html:141 <p class="text-sm text-gray-600">{% trans "We help with preparation and optimization." %}</p>
- templates/core/product_page.html:155 {% trans "Tell us what you need and get a proposal quickly. We handle the rest." %}
- templates/core/services.html:510 {% trans "We analyze your needs and objectives" %}
- templates/pages/websites/custom_website_plan.html:209 {% trans "We start with your goals, then design and build a site that fits your business." %}
- templates/pages/websites/custom_website_plan.html:309 {% trans "Every custom website is different. We define scope first, then quote clearly." %}
- templates/pages/websites/custom_website_plan.html:324 {% trans "We'll respond with a clear proposal and next steps." %}

## i18n Hardcoded String Findings
- templates/controlpanel/base_controlpanel.html:64 JCW_12
- templates/controlpanel/dashboard.html:9 Control Panel
- templates/controlpanel/dashboard.html:15 Control Panel
- templates/controlpanel/dashboard.html:16 Staff-only dashboard for core system objects.
- templates/controlpanel/dashboard.html:26 Pages
- templates/controlpanel/dashboard.html:31 Sections
- templates/controlpanel/dashboard.html:36 Sidebar Panels
- templates/controlpanel/dashboard.html:41 Features
- templates/controlpanel/dashboard.html:46 Managed Sites
- templates/controlpanel/dashboard.html:54 Latest media upload
- templates/core/billing.html:115 Plans
- templates/core/billing.html:116 Choose the plan that fits your business.
- templates/core/billing.html:130 Current plan
- templates/core/billing.html:132 Subscribe
- templates/core/billing_cancel.html:112 Plans
- templates/core/billing_cancel.html:113 Choose the plan that fits your business.
- templates/core/billing_cancel.html:127 Current plan
- templates/core/billing_cancel.html:129 Subscribe
- templates/core/billing_checkout.html:111 Plans
- templates/core/billing_checkout.html:112 Choose the plan that fits your business.
- templates/core/billing_checkout.html:126 Current plan
- templates/core/billing_checkout.html:128 Subscribe
- templates/core/billing_portal.html:111 Plans
- templates/core/billing_portal.html:112 Choose the plan that fits your business.
- templates/core/billing_portal.html:126 Current plan
- templates/core/billing_portal.html:128 Subscribe
- templates/core/billing_success.html:48 Go to dashboard
- templates/core/billing_success.html:112 Plans
- templates/core/billing_success.html:113 Choose the plan that fits your business.
- templates/core/billing_success.html:127 Current plan
- templates/core/billing_success.html:129 Subscribe
- templates/core/printful.html:51 Settings
- templates/core/right_sidebar.html:8 JustCodeWorks
- templates/dashboard/base_dashboard.html:127 JCW_12
- templates/dashboard/control_panel.html:7 Control Panel
- templates/dashboard/control_panel.html:8 Coming soon.
- templates/ops/base.html:32 JCW Operator Control Panel

## Services Page Note
- template: templates/core/services.html
- includes: none

## Conclusion
Ready to lock: NO
Reasons:
- placeholder/risky copy findings present
- hardcoded strings not wrapped for i18n
- orphan templates/partials detected