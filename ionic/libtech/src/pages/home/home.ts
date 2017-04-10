import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    welcomeMessage: string;
    user: any;
    panchayatsPage = PanchayatsPage;
    panchayats = ['MAHANTMANIYARI', 'RATNAULI']; // Placeholder for list of panchayats to fetch
    panchayatSelected = [false, false]; // Placeholder for list of panchayats to fetch

    constructor(public navCtrl: NavController) {
        window.localStorage.removeItem('user'); // Mynk this needs to go!
        if (!this.isLoggedIn()) {
            this.welcomeMessage = 'You are not logged in!';
            console.log(this.welcomeMessage);
            this.navCtrl.push(LoginPage);
        }
        else { // Mynk - This never gets called. The navPop() just returns back
            this.user = JSON.parse(window.localStorage.getItem('user'));
            console.log(JSON.stringify(this.user));
            this.welcomeMessage = 'Hi!';
        }
    }

    gotoPanchayat(selected, index, panchayat) {
        console.log(selected);
        console.log(panchayat);
        this.panchayatSelected[index] = !this.panchayatSelected[index];
        //        this.navCtrl.push(PanchayatsPage)
    }

    isLoggedIn() {
        if (window.localStorage.getItem('user')) {
            if (!this.user) {
                this.user = JSON.parse(window.localStorage.getItem('user'));
                console.log(JSON.stringify(this.user));
                this.welcomeMessage = 'Hi!';
            }
            return true;
        }
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }
}
