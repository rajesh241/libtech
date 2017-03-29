import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import { AuthProviders, AuthMethods, AngularFire } from 'angularfire2';

@Component({
    selector: 'page-login',
    templateUrl: 'login.html'
})
export class LoginPage {
    email: string;
    password: string;

    constructor(public navCtrl: NavController, public navParams: NavParams, private af: AngularFire) { }

    ionViewDidLoad() {
        console.log('ionViewDidLoad LoginPage');
    }

    login() {
        this.af.auth.login({
            email: this.email,
            password: this.password
        }, {
                provider: AuthProviders.Password,
                method: AuthMethods.Password
            }).then((response) => {
                console.log('Login Success' + JSON.stringify(response));
                let currentUser = {
                    email: response.auth.email,
                    picture: response.auth.photoURL
                };
                window.localStorage.setItem('currentUser', JSON.stringify(currentUser));
                this.navCtrl.pop();
            }).catch((error) => {
                console.log(error);
            });
    }
}
