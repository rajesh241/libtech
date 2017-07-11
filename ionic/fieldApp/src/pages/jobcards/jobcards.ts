import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable } from 'angularfire2-offline/database';
import { TransactionsPage } from '../transactions/transactions';

@Component({
    selector: 'page-jobcards',
    templateUrl: 'jobcards.html'
})
export class JobcardsPage {
    transactionsPage = TransactionsPage;
    panchayatSlug: string;
    // jobcardCode: string;
    jobcardsObservable: AfoListObservable<any[]>;
    totalJobcards: Number;
    items: any;
    jobcards: any;
    url = '/jcs/';
    expanded: any;
    expandHeight;
    // jobcardSlug: string;

    constructor(private navCtrl: NavController, private navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
	console.log('Inside Jobcards Constructor');
	this.expanded = {};
	this.expandHeight = 40;
        this.panchayatSlug = this.navParams.get('panchayatSlug');
        // this.jobcardCode = this.navParams.get('jobcardCode');
        // this.url += this.jobcardCode;
        // this.jobcards = afoDatabase.list(this.url);
        console.log(this.url + this.panchayatSlug); // + this.jobcardCode);
        this.jobcardsObservable = afoDatabase.list(this.url, {
            query: {
                orderByChild: 'panchayatSlug',
                equalTo: this.panchayatSlug
            }
        }); // .map((jobcard):AfoListObservable<any> => {jobcard[expanded] = false; console.log(jobcard); return jobcard;});
	this.jobcardsObservable.subscribe(items => {
	    this.items = items;
	    console.log(this.items);
	    this.items.forEach(jobcard => this.expanded[jobcard] = false);
	});
    }

    expandJobcards(jobcard) {
	this.expanded[jobcard] = !this.expanded[jobcard];
    }

    goHome() {
        this.navCtrl.popToRoot();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad JobcardsPage');
    }
}
