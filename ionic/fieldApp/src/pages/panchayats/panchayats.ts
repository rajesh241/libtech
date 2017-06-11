import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { JobcardsPage } from '../jobcards/jobcards'


@Component({
    selector: 'page-panchayats',
    templateUrl: 'panchayats.html'
})
export class PanchayatsPage {
    jobcardsPage = JobcardsPage;
    panchayats: any;

    constructor(public navCtrl: NavController, private navParams: NavParams) {
        this.panchayats = navParams.data;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad PanchayatsPage');
        this.panchayats = this.navParams.data;
        console.log(this.panchayats);
        console.log(JSON.stringify(this.panchayats))
    }

    goHome() {
        this.navCtrl.popToRoot();
    }
}
