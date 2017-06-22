import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

@IonicPage()
@Component({
    selector: 'page-profile',
    templateUrl: 'profile.html',
})
export class ProfilePage {
    user: any;
    
    constructor(public navCtrl: NavController, public navParams: NavParams) {
        this.user = this.navParams.data;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ProfilePage');
    }

    editPanchayaList() {
    }
    
    goHome() {
        this.navCtrl.popToRoot();
    }
}
