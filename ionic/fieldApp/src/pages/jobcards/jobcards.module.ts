import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { JobcardsPage } from './jobcards';

import { ExpandableComponent } from '../../components/expandable/expandable';
import { KeysPipe } from '../../pipes/keys/keys';

@NgModule({
  declarations: [
      JobcardsPage,
      ExpandableComponent,
      KeysPipe
  ],
  imports: [
    IonicPageModule.forChild(JobcardsPage),
  ],
  exports: [
    JobcardsPage
  ]
})
export class JobcardsPageModule {}
