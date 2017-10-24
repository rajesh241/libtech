import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { JobcardsPage } from './jobcards';

@NgModule({
  declarations: [
    JobcardsPage,
  ],
  imports: [
    IonicPageModule.forChild(JobcardsPage),
  ],
  exports: [
    JobcardsPage
  ]
})
export class JobcardsPageModule {}
