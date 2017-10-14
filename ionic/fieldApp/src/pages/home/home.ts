import { Component } from '@angular/core';

import { IonicPage, NavController } from 'ionic-angular';
import { PanchayatsPage } from '../panchayats/panchayats';
import { ProfilePage } from '../profile/profile';

import { AuthProvider } from '../../providers/auth/auth';

@IonicPage()
@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    user: any;
    panchayatsPage = PanchayatsPage;
    profilePage = ProfilePage;
    loginPage = 'LoginPage';

    constructor(public navCtrl: NavController, private auth: AuthProvider) {
        this.user = this.auth.getUser();
        if (!this.user) {
	    console.log('Should NOT be here');
	    this.navCtrl.setRoot('LoginPage');
        }
        console.log('After Login');
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

    hardReset() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations()
                .then(registrations => {
                    for (let registration of registrations) { registration.unregister() };
                    console.log('service worker installed');
                })
                .catch(err => console.log('Error', err));
        }
        else
            alert('Should NOT reach here!');
        window.localStorage.removeItem('user');
        window.location.reload(true)
    }

    logout() {
        this.auth.logout();
    }
}
