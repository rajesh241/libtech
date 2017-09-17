import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { AngularFireOfflineDatabase, AfoListObservable, AfoObjectObservable } from 'angularfire2-offline/database';
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
    metaObservable: AfoListObservable<any[]>;
    finyear16Observable: AfoListObservable<any[]>;
    finyear17Observable: AfoListObservable<any[]>;
    finyear18Observable: AfoListObservable<any[]>;
    dayOrMoreObservable: AfoListObservable<any[]>;
    metaObject: AfoObjectObservable<any>;;
    meta: any;
    items: any;
    jobcards: any;
    url = '/jobcards/';
    expanded: any;
    expandHeight;
    // jobcardSlug: string;

    constructor(private navCtrl: NavController, private navParams: NavParams, private afoDatabase: AngularFireOfflineDatabase) {
	console.log('Inside Jobcards Constructor');
	this.expanded = {};
	this.expandHeight = 40;
        this.panchayatSlug = this.navParams.get('panchayatSlug');
	this.url += this.panchayatSlug
        console.log(this.url);
        this.jobcardsObservable = afoDatabase.list(this.url, {
            query: {
		orderByKey: true
            }
        }); // .map((jobcard):AfoListObservable<any> => {jobcard[expanded] = false; console.log(jobcard); return jobcard;});
	this.jobcardsObservable.subscribe(items => {
	    this.items = items;
	    console.log(this.items);
	    this.items.forEach(jobcard => this.expanded[jobcard] = false);
	});

	this.metaObservable = this.afoDatabase.list('/panchayat_summary/' + this.panchayatSlug + '/'); // + '75daysOrMore')
        console.log('Meta is ');
        console.log(this.metaObservable);

	this.finyear16Observable = this.afoDatabase.list('/panchayat_summary/' + this.panchayatSlug + '/' + 'financial_year_2015-16'); // + '75daysOrMore')
        console.log('financial_year_2015-16 is ');
        console.log(this.metaObservable);

	this.finyear17Observable = this.afoDatabase.list('/panchayat_summary/' + this.panchayatSlug + '/' + 'financial_year_2016-17'); // + '75daysOrMore')
        console.log('financial_year_2016-17 is ');
        console.log(this.metaObservable);

	this.finyear18Observable = this.afoDatabase.list('/panchayat_summary/' + this.panchayatSlug + '/' + 'financial_year_2017-18'); // + '75daysOrMore')
        console.log('financial_year_2017-18 is ');
        console.log(this.metaObservable);

	this.dayOrMoreObservable = this.afoDatabase.list('/panchayat_summary/' + this.panchayatSlug + '/' + '75daysOrMore');
        console.log('dayOrMoreObservable is ');
        console.log(this.dayOrMoreObservable);

        this.metaObject = this.afoDatabase.object('/panchayat_summary/' + this.panchayatSlug + '/'); // + '75daysOrMore');
        this.metaObject.subscribe(meta => {
            console.log('MetaObject is ');
            console.log(meta);
            this.meta = meta;
        })
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
