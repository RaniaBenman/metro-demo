# Demo runbook: Replicate's pricing in Metronome (30 min)


| Customer | Offering | Link |
|---|---|---|
| Ada Okafor | Free trial ($10, 30 days) | https://app.metronome.com/customers/d44c4fc0-a5cf-4069-82d4-5a48daf4af7c |
| Brightframe AI | Pay-as-you-go + Pro Support | https://app.metronome.com/customers/10a372d9-6bd7-4984-886d-a24ac14994ca |
| Northwind Media | $100k prepaid commit, 3 years | https://app.metronome.com/customers/a162a702-1a41-43c1-92d9-f28d7f6615cf |
| Kepler Games | $100k postpaid minimum, 3 years | https://app.metronome.com/customers/27da32a3-451b-48fb-ba14-84f252556716 |
https://docs.google.com/presentation/d/1HdrACtg-SPn5qvqFiTN043FZZF6ojzNDiABUA-67xo0/edit?slide=id.p6#slide=id.p6

 Basics
 - https://app.metronome.com/events?startingOn=2026-09-18T00%3A00%3A00.000Z&endingBefore=2026-10-18T00%3A00%3A00.000Z
 - https://app.metronome.com/offering/billable-metrics/7390320d-c651-473d-b6b6-3817f804bec0
 - https://app.metronome.com/offering/products?product_id=6c2ba938-efe8-4261-9dad-6d71dad49d6d
 - https://app.metronome.com/offering/rate-cards/a9fd7428-fdaa-4b53-9770-1a76fdd04f0c

Ada Alerts
- https://app.metronome.com/customers/d44c4fc0-a5cf-4069-82d4-5a48daf4af7c/invoices/cec50b47-a4fa-5adb-914e-45b0799cb534
- https://app.metronome.com/developer/notifications

Customers
- https://app.metronome.com/customers/10a372d9-6bd7-4984-886d-a24ac14994ca/invoices/a6327a8e-2267-5054-b617-6322b3515a5e
- https://app.metronome.com/customers/a162a702-1a41-43c1-92d9-f28d7f6615cf/invoices/aff1e1e8-f635-5473-9ef0-5f418ef9352a

Integration:
- https://app.metronome.com/developer/integrations

Misc:
- https://app.metronome.com/offering/packages
- https://app.metronome.com/customers/27da32a3-451b-48fb-ba14-84f252556716/invoices/e665caa2-bf33-59ce-a0dd-076b869e84d1


## Before the demo

1. **Within the hour before the demo:** `./run_single.sh 06_dashboard_links.py`. The customer dashboard links expire 1 hour after they're generated.

## Act 0: one event, every price (2 min)

- **INTRO :** So.... before we jump into the gist of it (with customers , and invoices , and whatnot) >>> let me show you where it ALL starts.... : It starts from ONE single thing , which we call : a usage event.

- **SHOW:**
	- ((==🟢**events** - LAST transaction))== 
	  every time one of your machines runs a prediction , a deployment , a training job.... the Replicate app sends Metronome one of THESE : ... An event ... It tells us :
		  - What customer ran that inference,
		  - HOW LONG it ran (in `seconds`),
		  - on WHICH `hardware`(gpu-a100, gpu-x).... etc....
	  --> so  ==🟡ONE event type, for EVERYTHING Replicate meters== , whatever the GPU, whatever the model 
	  
	- Then we have the ==🟢**billable metric** ((*Compute seconds))*== : basically, it's ==🟡WHAT we COUNT== from those events , and how we can slice it .... :
	  ... so in Replicate's case, thats a ==🟡sum of `seconds`, grouped by `hardware`==  (.... +we can throw in  `model` too for the breakdowns... the type of `workload` ...etc.)

	- on top of the events, the metric.... we just need TWO more foundational building blocks:
		- a ==🟢**product**== >>> what you actually ==🟡SELL==.... the line that your customer reads on their invoice
		- a ==🟢**rate card**== >>> basically your ==🟡price list==.... with the 'list prices' that EVERY customer starts from(before their own contract terms kick in ... be it by a discount during a commit ... a free credit , etc...) 
		  
	- --> so all in all.... ==🟡events IN.... prices OUT== >>> let's dive in now

## Act 1 (2mn): 

-
- **SHOW:** 
	- ((==🟢 "*Compute hours"* product==)): one of the core products that Replicate sells is USAGE of your hardware.... NOT the hardware itself .... it's TIME  on that hardware (not the gpu itself)
	- ((==🟢rate card== )) so in our rating card :
		- we're rating time ... in Replicate's case: it's  HOURS (...mind you the events we receive count for seconds... so we set a  ==🟡conversion to go from seconds to hours ==) ....
		- (so we rate hours) and the way we ==🟡rate those hours, that usage, is per GPU== , according to the pricing model you provide
	  --> and you kiiiiinda start to see what i'm getting at :   gpus/hardware becomes nothing but a pricing dimension 
	  --> that meeeeans , billing-wise,  a gpu launch..  now translates to a  ONE simple additional line in this card of rates ....
	  (oone gpu . one price)... ZERO code change in your app ....
	  
	  ...and we'll even do this live in a few minutes
	   but for now, if you take a look, you'll see >>> :
		 -  your ==🟡7 existing== gpu types >>> 
		 - a couple of  additional ones (`gpu-99`,  `gpu-l40s` ), just dummy ones we added before the demo.
		 -  +(more importantly) ==🟡2 types of Support Tiers== >>>:
			- one at a fixed fee, 
			- one at a % of the usage,
			which we'll get to in a second when we look at the invoices

  - Screens:
	  - [act1_product_compute-hours](screens/act1_product_compute-hours.jpg), 
	  - [act1_rate-card_replicate-list-prices_after-l40s](screens/act1_rate-card_replicate-list-prices_after-l40s.jpg).
## Act 2: Free trial credit LEAK (3mn/30)

- **SHOW:** ((==🟢Customer invoices==)) 
  so all these usage rates , and support rates ... are reflected in your customer invoices, according to their specific contract terms : 
	  
	- Here we have the current period's draft invoice for ==🟢Ada==, a ==🟡newly-signed-up== paygo customer, 
	  which had benefited from ==🟡free trial credit==... 
	  ((BOTTOM RIGHT)) in this example, we see that the credit is fully consumed.... and resulted in an ==🟡overrage== to be paid in ==🟡arrears== in classic paygo motion....
	  
	  the size of that overrage depends on>>>> :
		- whether she provided a credit card for example ( and was then allowed to continue consuming).... 
		- ORR how fast we cut off access after we're notified of the exhaustion of her free credit with no card on file. >>>>>

	  Our understanding is that :  With ==🟡Replicate's current system==, that exhaustion ==🟡detection takes AT LEASSSST 24-hours==...... --> thats a  24hour-long cost leak >>>>>
	  
	   /!\ ==🟢((Ada's alerts==)) On Metronome....BECAUSE it allows you to set thresholds and evaluates them every 3 minutes... it is able to fire ==🟡alerts for your application, within FIIIIVE minutes== of your Replicate usage events arriving to Metronome>>>>>
	   ((configured vs TRIGGERED)) .... In the case of Ada, we see that:
		   -  ==🟡2 of the alerts== that we configured , have been fired (*Trial credit: 20% left* + *credit exhausted*)
		   - and that alerts like *Trial ends in 3 days* is OK
	- Screens: [act2_ada_app_alerts-in-alarm](screens/act2_ada_app_alerts-in-alarm.jpg).

- **SHOW:** ==🟢Developer → Notifications==: 
	- These alerts arent limited to Ada. They can be configured at a ==🟡higher level== to target specific events, conditions, and objects tagged in a certain way --> So those same trial credit alerts we mentioned for Ada, actually cover (in this example) every paygo customer (since they filter on the credit's tag). 
	  
	- That said... you can also get in the nitty-gritty .... and ==🟡track your most strategic== and critical customers... by creating alerts that target them specifically ((FIRST)) like we did here here with Brightframe
  - Screens: [act2_developer_notifications-account-wide](screens/act2_developer_notifications-account-wide.jpg).

- /////TODO where is alert tag defined + temp using excel with input start time and a formula for each section based on target duration
  

## Act 3: Support tiers (3:30mn)

- ((CHECKPOINT)) ...... So :
	-  we talked about new GPU launch
	- we addressed the cost leakage CAUSED BY the long delays in credit exhaustion detection .....
	--> .......Let's now talk about how Metronome can help you model your  support tiers, and basically open new doors for you to  additional sources of revenue

- Here we have the invoice draft for ANOTHER ==🟡paygo customer== : fictional company we call ==🟢Brightframe== >>>
	  -/!\ ==🟢((TOP Oct01-Nov01))==  one line per machine type, same ==🟡list prices== as Ada.... 
	  -/!\ ==🟢((Oct1 finalized))== but who ALSO has purchased a ==🟣((prod+rate+package))== ==🟡support subscription==... at the  fixed fee of 500USD/month... a fee we can see here  ---/!\ ((==🟢TOP overview > MIDDLE contracts > MIDDLE subscription > TOP of chart ==)) is  billed in ==🟡advance==.............
  --> so... :
	- ==🟡**usage** billed in **arrears** (classic paygo motion)==
	- ==🟡**subscription** billed in **advance** (at a fixed rate)==
	  ...........>>>>
	  
- Here, we have a THIRD customer ==🟢Northwind==, which unlike Ada & Brightframe : 
	  -/!\ ==🟢((Oct1))== is NOT a paygo customer , but one that has signed a ==🟡COMMIT== with us of 100K.. prepaid upfront in ==🟡3 yearly installments== >>> (we see the 3 draft invoices) >>>
		- of 2028, 
		- 2027 
		- and a finalized one for the current year 2026
	  -/!\ ==🟢((Oct01-Nov01))== and since they signed a commit... that ==🟡commit pays the compute== they use (as we can see here in the draft invoice)
	  ((FAR RIGHT)) and if you look closer , you'll see that Metronome also helped us model for our commit customers  :
		- a ==🟣((contract override w multiplier))== ==🟡15% discount==  on the list prices (which brings cpus price to 0.31/h down from of 0.36, and so on)
		- aaaand  ((BOTTOM LEFT)) ==🟣((prod w composite_tags on compute +rate))== metronome also helped us set up a  ==🟡support tier billed as a %== of their usage. (....here 10%) ... unlike Brightframe , the paygo customer that has support tier at a FIXED rate....
	
	
- --> so...... 
	- a ==🟡fixed tier== for grow***ing*** paygo teams... 
	- and a ==🟡percentage tier== that grows with **enterprise** usage that are on commit......
	---> and these are just TWOOO examples ... of the level of FLEXIBILITY you get on Metronome, to serve and support your customers


---------------------------HALF TIME-------------------------

## Act 4: Commit consumption (2mn)


- ((CHECKPOINT)) ...... So :
	-  we talked support tiers
	- talked about new GPU launch
	- we addressed the exhausted free trial credit cost leakage 
	--> .......Let's switch perspectives for a moment now.... and see things from the customer's point of view
	
...i know you mentioned you 're having difficulty ==🟡telling your commit customers where they are against their commit==, without the manual labor of having an engineer pull data everytime from the database :

- 1- Well with Metronome, your teams can build custom dashboards right in the Replicate app, that ==🟡call Metronome's APIs== in the the background, to automatically get the latest usage data , the latest commit consumption data , for your customers dashboards... :
  (it can be a ca;; to the `listbalance` endpoint , it can be the `usage` endpoint)... depending on which information you want to expose to your users, we can help you identify the right Metronome API endpoint to call , that addresses your need
  
- 2- ==🟢((EMBED-LAST))== Another no-fuss alternative would be to use Metronome's sorta ==🟡plug&play interactive embeded dashboards== like this one  right here, directly into your app, with minimal to no maintenance work at all : just a simple authenticated iframe-ready dynamically-generated URL... (which imo are a GREAT way imo to ==🟡bootstrap in no time the initial experience== as you refine it along the way)

## BONUS / FLASH : LIVE LAUNCH (5mn)

- **TRANSITION :** NOW that we looked at some invoices (which rememebrr... :
	- are calculated based on usage events we received from the Replicate app
	- every inference event would carry as we saw earlier :
	   - the customer identifier, 
	   - the number of seconds, 
	   - the hardware on which that inference was run (and which will help us determine its price), etc.	 
	
	so now that we seen these invoices... it's worth to mention that.. for THIS demo ...amooooong the events we sent to Metronome... we *plaaaanted* a few  ones carrying the identifier of a NEWLY launched hardware (hypothetically , we called it GPU-h100) >>>> ==🟡A hardware that we haven't  priced in yet== in the ==🟢rate card,== (it has NOOO price) , and thus ISN'T accounted for, in all these draft invoices we saw.
	
	So , in other words, our engineers on the Replicate app side, went ahead and innovated in an agile way, did their hardware launch on the app, users started using it.... and on Metronome we started receiving those usage events with that new hardware tag ...
  
 - **LIVE:**  So what we'll do in this part of the demo, is launch together the billing of GPU-h100, to illustrate how your app can independently launch its hardware, and move LEANLY-AND-FREELY...  withOUT being hurdled by billing mechanics which we'll take care of... here... together ... ASYNCHRONOUSLY :
	- ==🟢Offering → Rate cards → Replicate list prices → **+ Add a rate**== (top right):
	  - product **Compute hours**;
	  - `hardware` = **gpu-h100**;
	  - **$5.49** per hour;
	  - starting **Oct 1, 2026 (UTC)**;
	  - entitled.
	  ((**Fallback:** `./run_single.sh 05_launch_gpu.py --hardware gpu-h100` adds the same rate by API.))

- **EFFECT:** Now that we officially launched our GPU-H100, let's refresh our  :
	- /!\ (==🟢(Oct01-Nov01)) Brightframe=='s invoice --> ... see how it gains an H100 line & updates the total,
	- /!\ ==🟢((Oct01-Nov01 Northwind== : 
		- also a new line
		- ((FAR RIGHT)) ==🟣((contract override w multiplier))== automatically at 15% off given the commit... 
		- ((BOTTOM)) ==🟣((prod w composite_tags on compute +rate))== support fee aligned with it>>>>>
	  
	aaaaall with :
	- ZERO code change to the Replicate app 
	- no usage missed since the launch on the app
	-  no launch delayed >>> no revenue delayed >>>
	- and the company remains COMPETITIVE during new trends and major hardware releases




## Act 5: quote-to-cash flow

- **SHOW:** ==🟢Developer → Integrations==((SPEAK)) :
	- Stripe collects the payments,
	- Salesforce gets a daily sync of your contracts, commits, etc
		- FYI : enterprise contracts store their opportunity ID in an `sfdc_opportunity_id` custom field. Metronome's own Salesforce field needs the integration connected
	- NetSuite (Public Beta) invoices your enterprise customers
	