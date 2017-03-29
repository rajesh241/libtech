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
    panchayatsPage = PanchayatsPage;
    panchayats = []; // Placeholder for list of panchayats to fetch

    constructor(public navCtrl: NavController) {
        window.localStorage.removeItem('currentUser'); // Mynk this needs to go!
        if (!this.isLoggedIn()) {
            this.welcomeMessage = 'You are not logged in';
            console.log(this.welcomeMessage);
            this.navCtrl.push(LoginPage);
        }
        else {
            this.welcomeMessage = 'Please select the panchayats you wish to follow';
        }
    }
    gotoPanchayats() {
        this.navCtrl.push(PanchayatsPage)
    }

    isLoggedIn() {
        if (window.localStorage.getItem('currentUser')) {
            return true;
        }
    }
}
