import { Component } from '@angular/core';
import { IonicPage,
	 NavController,
	 NavParams,
	 LoadingController,
	 Loading
       } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';

import { AlertController } from 'ionic-angular';

@IonicPage()
@Component({
    selector: 'page-transaction',
    templateUrl: 'transaction.html'
})
export class TransactionPage {
    jobcard: string;
    key: string;
    transaction: string;
    url: string;
    remarks: string;
    // complaint: any;
    updated = true;
    complaintUpdated = true;
    field: AfoListObservable<any>;
    parent: AfoListObservable<any>;
    loading: Loading;
    complaint: any;
    complaintTypes: any;
    complaintDesc: string;

    constructor(public navCtrl: NavController,
		public navParams: NavParams,
		private afoDatabase: AngularFireOfflineDatabase,
                private alertCtrl: AlertController,		
		private loadingCtrl: LoadingController) {
        this.jobcard = this.navParams.get('jobcard');
        this.key = this.navParams.get('key');
        this.transaction = this.navParams.get('transaction');
        this.url = this.navParams.get('url');
        this.parent = this.afoDatabase.list(this.url);
        this.url += '/' + this.key;
        console.log(this.url);
        this.field = this.afoDatabase.list(this.url);
        console.log('Field :');
        console.log(this.field);
        this.complaint = { desc: '', types: [] };
        this.complaintTypes = [
                'जॉब कार्ड जारी न किया जाना',
                'जॉब कार्ड से सम्बंधित अन्य शिकायतें',
                'मस्टर रोल में जालसाजी',
                'मस्टर रोल सम्बंधित अन्य शिकायत',
                'काम की मांग या आवंटन से सम्बंधित',
                'मेट से सम्बंधित',
                'कार्यों के चयन में ग्राम सभा को शामिल न किया जाना',
                'योजना के लाभार्थियों के चयन में अनियमितताएं',
                'योजना के नियोजन, स्वीकृति या गुणवत्ता से सम्बंधित',
                'ऐसे कार्य करना जिनकी अनुमति नहीं है',
                'कार्यस्थल सुविधा सम्बंधित',
                'निर्धारित प्रक्रिया का अनुपालन किये बिना सामग्री खरीदना',
                'सामग्री सम्बंधित सुझाव/ याचिकाएं',
                'मजदूरी भुगतान/मुआवजा सम्बंधित',
                'बेरोज़गारी भत्ता न दिया जाना',
                'मशीनों का उपयोग',
                'बैंक सम्बंधित',
                'सामाजिक अंकेक्षण न किया जाना',
                'घूंस या चोरी की शिकायत / वित्तीय अनियमितताएं',
                'किसी कर्मी/अधिकारी के विरुद्ध काम न करने की शिकायत',
                'याचिकाएं (मजदूरी दर बढ़ाना, कार्यों की नयी श्रेणी शामिल करना, अन्य कार्यक्रमों से तालमेल, कार्यदिवस बढ़ाना, भ्रष्टाचार कम करना इत्यादि)',
                'एक ही शिकायत में एक से अधिक मुद्दे',
                'अन्य मुद्दा'
        ];
    }

    remarksUpdate() {
	this.presentSpinner('Updating records...');
        if (this.remarks) {
	    let date = new Date().getTime()
            this.parent.update(this.key, { remarks: this.remarks, timeStamp: date });
	}
        this.updated = true;
	this.loading.dismiss();
    }

    createComplaint(complaint) {
        let alert = this.alertCtrl.create();
        alert.setTitle('Create Complaint');

        if(!complaint)
            complaint = {types: []};
        else
            console.log('Prepopulated Complaint ' + JSON.stringify(complaint));
        console.log('Complaint:');
        console.log(complaint);
        // this.complaintTypes = [ 'Type A', 'Type B', 'Type C', 'Type D'];

        this.complaintTypes.forEach(type => {
            console.log('Type ' + JSON.stringify(type));
            alert.addInput({
                type: 'checkbox',
                label: type,
                value: type,
                checked:  (complaint.types.indexOf(type) != -1) // type in complaint.types //
            });
        });

        alert.addButton('Cancel');
        alert.addButton({
            text: 'Okay',
            handler: data => {
                console.log('Data Handler: ');
                console.log(JSON.stringify(data));
                console.log('Data ' + data);
                // data.forEach(type => { console.log('For this Type - ' + type); complaint.types[type] = type; console.log('This Type ' + complaint.types[type]) });
                // complaint.typesArray = [] // this.dictToArray(complaint.types)
                // console.log(complaint.typesArray);
                let date = new Date().getTime();
                complaint.timeStamp = date;
                if(this.complaintDesc)
                   complaint.desc = this.complaintDesc;
                complaint.types = data;
                console.log('Final Complaint ' + JSON.stringify(complaint));
                this.complaint = complaint;
                this.complaintUpdated = false;
                this.complaintUpdate();
            }
        });
        alert.present();
    }

    complaintUpdate() {
	this.presentSpinner('Updating complaint...');
        this.parent.update(this.key, { complaint: this.complaint });
        this.complaintUpdated = true;
	this.loading.dismiss();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionPage');
        console.log(this.url);
        console.log(this.jobcard);
        console.log(this.key);
    }

    presentSpinner(msg) {
	this.loading = this.loadingCtrl.create({
	    content: msg,
	    dismissOnPageChange: true,
	});

	this.loading.present();
    }
    
    goHome() {
        this.navCtrl.popToRoot();
    }
}
