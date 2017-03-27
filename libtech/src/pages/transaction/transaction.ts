import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { AngularFire, FirebaseListObservable } from 'angularfire2';

@Component({
    selector: 'page-transaction',
    templateUrl: 'transaction.html'
})
export class TransactionPage {
    jobcard: string;
    date: string;
    transaction: string;
    url: string;
    remarks: string;
    createComplaint = false;
    updated = true;
    field: FirebaseListObservable<any>;


    constructor(public navCtrl: NavController, public navParams: NavParams, private af: AngularFire) {
        this.jobcard = this.navParams.get('jobcard');
        this.date = this.navParams.get('date');
        this.transaction = this.navParams.get('transaction');
        this.url = this.navParams.get('url') + '/' + this.date;
        console.log(this.url);
        this.field = this.af.database.list(this.url);
        console.log(this.field);
    }

    onCreateComplaint(event) {
        alert(JSON.stringify(event));
        console.log(JSON.stringify(event)); // + createComplaint);
    }

    update(event) {
        console.log(JSON.stringify(event) + this.createComplaint + '==' + this.remarks); // Can skip this.remarks Mynk
        // this.field.update("1", { remarks: remarkInput.value });
        if (this.remarks)
            this.field.update("1", { remarks: this.remarks });
        this.field.update("1", { createComplaint: this.createComplaint });
        this.updated = true;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad TransactionPage');
    }


    goHome() {
        this.navCtrl.popToRoot();
    }
}
