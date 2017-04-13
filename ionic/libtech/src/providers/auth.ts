import { Injectable } from '@angular/core';
import { AngularFire, AuthProviders, AuthMethods } from 'angularfire2';

@Injectable()
export class Auth {
    user: any;

    constructor(public af: AngularFire) {
        console.log('Hello Auth Provider');
    }

    isLoggedIn() {
        if (window.localStorage.getItem('user')) {
            if (!this.user) {
                this.user = JSON.parse(window.localStorage.getItem('user'));
                console.log(JSON.stringify(this.user));
            }
            return true;
        }
    }

    getUser() {
        if (window.localStorage.getItem('user')) {
            if (!this.user) {
                this.user = JSON.parse(window.localStorage.getItem('user'));
                console.log("Fetched User [" + JSON.stringify(this.user) + "]");
            }
        }
        return this.user;
    }

    login(email, password) {
        return this.af.auth.login({
            email: email,
            password: password
        }, {
                provider: AuthProviders.Password,
                method: AuthMethods.Password
            }).then((response) => {
                console.log('auth ' + 'Login Success' + JSON.stringify(response));
                let user = {
                    email: response.auth.email,
                    picture: response.auth.photoURL
                };
                console.log('auth ' + JSON.stringify(user));
                window.localStorage.setItem('user', JSON.stringify(user));
            }).catch((error) => {
                console.log(error);
                alert(error);
            });
    }

    loginWithGoogle() {
        return this.af.auth.login({
            provider: AuthProviders.Google,
            method: AuthMethods.Popup
        }).then((response) => {
            console.log('Login with Google Success' + JSON.stringify(response));
            let user = {
                email: response.auth.email,
                picture: response.auth.photoURL
            };
            console.log(JSON.stringify(user));
            window.localStorage.setItem('user', JSON.stringify(user));
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    loginWithFacebook() {
        return this.af.auth.login({
            provider: AuthProviders.Facebook,
            method: AuthMethods.Popup
        }).then((response) => {
            console.log('Login with Facebook Success' + JSON.stringify(response));
            let user = {
                email: response.auth.displayName,
                picture: response.auth.photoURL
            };
            console.log(JSON.stringify(user));
            window.localStorage.setItem('user', JSON.stringify(user));
        }).catch((error) => {
            console.log(error);
            alert(error);
        });
    }

    logout() {
        this.user = null;
        window.localStorage.removeItem('user');
        return this.af.auth.logout();
    }
}
