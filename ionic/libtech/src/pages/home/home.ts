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
    loginPage = LoginPage;
    panchayatsPage = PanchayatsPage;
    panchayats = ['MAHANTMANIYARI', 'RATNAULI']; // Placeholder for list of panchayats to fetch
    panchayatSelected = [false, false]; // Placeholder for list of panchayats to fetch

    constructor(public navCtrl: NavController, private auth: Auth) {
        window.localStorage.removeItem('user'); // FIXME Mynk this needs to go!
        if (!this.getUser()) {
            this.navCtrl.push(LoginPage);
        }
    }

    gotoPanchayat(selected, index, panchayat) {
        console.log(selected);
        console.log(panchayat);
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        //        this.navCtrl.push(PanchayatsPage)
    }

    getUser() {
        this.user = this.auth.getUser();
        return this.user;
    }

    logout() {
        this.auth.logout();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }
}
