import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

import { PanchayatsProvider } from '../../providers/panchayats/panchayats';

@IonicPage()
@Component({
    selector: 'page-edit-panchayats',
    templateUrl: 'edit-panchayats.html',
})
export class EditPanchayatsPage {
    user: any;
    panchayats: any;
    userPanchayats: any;
    preferredPanchayats: any[];

    constructor(public navCtrl: NavController, public navParams: NavParams,
		private panchayatsProvider: PanchayatsProvider) {
        console.log('Inside EditPanchayats Constructor');
        this.user = this.navParams.data;
        console.log('USER ' + JSON.stringify(this.user));
        this.userPanchayats = this.user.panchayats;
        console.log(this.userPanchayats);
        this.preferredPanchayats = Object.keys(this.userPanchayats).map(key => this.userPanchayats[key]);
        console.log(this.preferredPanchayats);
    }

    
    ionViewDidLoad() {
	console.log('ionViewDidLoad EditPanchayatsPage');
	this.panchayats = this.panchayatsProvider.list();
    }

}
