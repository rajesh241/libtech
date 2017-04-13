import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'

import { Auth } from '../../providers/auth';

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    user: any;
    panchayatsPage = PanchayatsPage;
    panchayats = ['MAHANTMANIYARI', 'RATNAULI']; // Placeholder for list of panchayats to fetch
    panchayatSelected = [false, false]; // Placeholder for list of panchayats to fetch

    constructor(public navCtrl: NavController, private auth: Auth) {
        window.localStorage.removeItem('user'); // FIXME Mynk this needs to go!
        if (!this.isLoggedIn()) {
            this.navCtrl.push(LoginPage);
        }
    }

    gotoPanchayat(selected, index, panchayat) {
        console.log(selected);
        console.log(panchayat);
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        //        this.navCtrl.push(PanchayatsPage)
    }

    isLoggedIn() {
        if (this.auth.isLoggedIn()) {
            this.user = this.auth.getUser();
            console.log('#### ' + JSON.stringify(this.user)); // FIXME
            return true;
        }
        return false;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }
}
