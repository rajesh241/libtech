import { Component } from '@angular/core';

import { IonicPage,
	 NavController,
	 LoadingController,
	 Loading
       } from 'ionic-angular';

import { AuthProvider } from '../../providers/auth/auth';

@IonicPage()
@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {
    user: any;
    panchayatsPage = 'PanchayatsPage';
    profilePage = 'ProfilePage';
    loginPage = 'LoginPage';
    loading:Loading;

    constructor(public navCtrl: NavController,
		private auth: AuthProvider,
		private loadingCtrl: LoadingController) {
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

    presentSpinner(msg) {
	this.loading = this.loadingCtrl.create({
	    content: msg,
	    dismissOnPageChange: true,
	});

	this.loading.present();
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
