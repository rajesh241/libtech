import { Component } from '@angular/core';

import { NavController } from 'ionic-angular';
import { LoginPage } from '../login/login';
import { PanchayatsPage } from '../panchayats/panchayats'
import { ProfilePage } from '../profile/profile'

import { Auth } from '../../providers/auth';

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    user: any;
    loginPage = LoginPage;
    panchayatsPage = PanchayatsPage;
    profilePage = ProfilePage;

    constructor(public navCtrl: NavController, private auth: Auth) {
        this.user = this.auth.getUser();
        if (!this.user) {
            this.navCtrl.push(LoginPage);
        }
        console.log('After Login');
        // Hard Refresh - window.location.reload(false)
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad HomePage');
    }

    ionViewDidEnter() {
        console.log('ionViewDidEnter HomePage');
    }

    getUser() {
        this.user = this.auth.getUser();
        return this.user;
    }

    logout() {
        this.auth.logout();
    }
}
