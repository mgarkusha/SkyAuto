# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models


class Carmodels(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CarModels'


class Cars(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    callsign = models.TextField(db_column='Callsign', blank=True, null=True)  # Field name made lowercase.
    idcolor = models.ForeignKey('Colors', models.DO_NOTHING, db_column='IDColor', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State')  # Field name made lowercase.
    idcurrentdriver = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='IDCurrentDriver', blank=True, null=True)  # Field name made lowercase.
    idparking = models.ForeignKey('Parkings', models.DO_NOTHING, db_column='IDParking', blank=True, null=True)  # Field name made lowercase.
    parknumber = models.IntegerField(db_column='ParkNumber', blank=True, null=True)  # Field name made lowercase.
    number = models.TextField(db_column='Number', blank=True, null=True)  # Field name made lowercase.
    # idclass = models.ForeignKey(Carclasses, models.DO_NOTHING, db_column='IDClass', blank=True, null=True)  # Field name made lowercase.
    idmodel = models.ForeignKey(Carmodels, models.DO_NOTHING, db_column='IDModel', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    todate = models.DateTimeField(db_column='TODate', blank=True, null=True)  # Field name made lowercase.
    terminaltype = models.IntegerField(db_column='TerminalType')  # Field name made lowercase.
    priority = models.BigIntegerField(db_column='Priority', blank=True, null=True)  # Field name made lowercase.
    # iddefaultparking = models.ForeignKey('Parkings', models.DO_NOTHING, db_column='IDDefaultParking', blank=True, null=True)  # Field name made lowercase.
    timeonline = models.DateTimeField(db_column='TimeOnline', blank=True, null=True)  # Field name made lowercase.
    timedisconnected = models.DateTimeField(db_column='TimeDisconnected', blank=True, null=True)  # Field name made lowercase.
    euroclass = models.IntegerField(db_column='EuroClass', blank=True, null=True)  # Field name made lowercase.
    statestarttime = models.DateTimeField(db_column='StateStartTime', blank=True, null=True)  # Field name made lowercase.
    # idmaindriver = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='IDMainDriver', blank=True, null=True)  # Field name made lowercase.
    releasetime = models.DateTimeField(db_column='ReleaseTime', blank=True, null=True)  # Field name made lowercase.
    allowautodistribution = models.IntegerField(db_column='AllowAutoDistribution', blank=True, null=True)  # Field name made lowercase.
    # idreleaseparking = models.ForeignKey('Parkings', models.DO_NOTHING, db_column='IDReleaseParking', blank=True, null=True)  # Field name made lowercase.
    releaselat = models.FloatField(db_column='ReleaseLat', blank=True, null=True)  # Field name made lowercase.
    releaselon = models.FloatField(db_column='ReleaseLon', blank=True, null=True)  # Field name made lowercase.
    idroadsidetariff = models.BigIntegerField(db_column='IDRoadsideTariff', blank=True, null=True)  # Field name made lowercase.
    terminalversion = models.TextField(db_column='TerminalVersion', blank=True, null=True)  # Field name made lowercase.
    defaultgroupid = models.BigIntegerField(db_column='DefaultGroupID', blank=True, null=True)  # Field name made lowercase.
    defaultparknumber = models.IntegerField(db_column='DefaultParkNumber', blank=True, null=True)  # Field name made lowercase.
    defaultordercount = models.IntegerField(db_column='DefaultOrderCount', blank=True, null=True)  # Field name made lowercase.
    isreadyforautoassignment = models.IntegerField(db_column='IsReadyForAutoAssignment', blank=True, null=True)  # Field name made lowercase.
    groupaccess = models.TextField(db_column='GroupAccess', blank=True, null=True)  # Field name made lowercase.
    passengersamount = models.IntegerField(db_column='PassengersAmount', blank=True, null=True)  # Field name made lowercase.
    idoldparking = models.BigIntegerField(db_column='IDOldParking', blank=True, null=True)  # Field name made lowercase.
    oldparkingnumber = models.IntegerField(db_column='OldParkingNumber', blank=True, null=True)  # Field name made lowercase.
    permissionnumber = models.TextField(db_column='PermissionNumber', blank=True, null=True)  # Field name made lowercase.
    passengerslastdate = models.DateTimeField(db_column='PassengersLastDate', blank=True, null=True)  # Field name made lowercase.
    waitingtime = models.DateTimeField(db_column='WaitingTime', blank=True, null=True)  # Field name made lowercase.
    idgps = models.BigIntegerField(db_column='IDGps', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'Cars'


class Corporations(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    fullname = models.TextField(db_column='FullName', blank=True, null=True)  # Field name made lowercase.
    inn = models.TextField(db_column='INN', blank=True, null=True)  # Field name made lowercase.
    bik = models.TextField(db_column='BIK', blank=True, null=True)  # Field name made lowercase.
    account = models.TextField(db_column='Account', blank=True, null=True)  # Field name made lowercase.
    kpp = models.TextField(db_column='KPP', blank=True, null=True)  # Field name made lowercase.
    bankaccount = models.TextField(db_column='BankAccount', blank=True, null=True)  # Field name made lowercase.
    contractnumber = models.TextField(db_column='ContractNumber', blank=True, null=True)  # Field name made lowercase.
    contractdatestart = models.DateTimeField(db_column='ContractDateStart', blank=True, null=True)  # Field name made lowercase.
    contractdatestop = models.DateTimeField(db_column='ContractDateStop', blank=True, null=True)  # Field name made lowercase.
    # idbilling = models.ForeignKey(Billings, models.DO_NOTHING, db_column='IDBilling', blank=True, null=True)  # Field name made lowercase.
    orderscounter = models.IntegerField(db_column='OrdersCounter', blank=True, null=True)  # Field name made lowercase.
    orderscanceled = models.IntegerField(db_column='OrdersCanceled', blank=True, null=True)  # Field name made lowercase.
    cashless = models.IntegerField(db_column='Cashless', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    # idlanguage = models.ForeignKey('Translationlanguages', models.DO_NOTHING, db_column='IDLanguage', blank=True, null=True)  # Field name made lowercase.
    keyword = models.TextField(db_column='Keyword', blank=True, null=True)  # Field name made lowercase.
    guid = models.TextField(db_column='GUID', blank=True, null=True)  # Field name made lowercase.
    checkcontractnumber = models.IntegerField(db_column='CheckContractNumber', blank=True, null=True)  # Field name made lowercase.
    checkkeyword = models.IntegerField(db_column='CheckKeyword', blank=True, null=True)  # Field name made lowercase.
    checkcostcentr = models.IntegerField(db_column='CheckCostCentr', blank=True, null=True)  # Field name made lowercase.
    canaddclients = models.IntegerField(db_column='CanAddClients', blank=True, null=True)  # Field name made lowercase.
    iddefaultservice = models.BigIntegerField(db_column='IDDefaultService', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Corporations'


class Drivers(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fullname = models.TextField(db_column='FullName')  # Field name made lowercase.
    employeetype = models.IntegerField(db_column='EmployeeType')  # Field name made lowercase.
    idcurrentcar = models.ForeignKey(Cars, models.DO_NOTHING, db_column='IDCurrentCar', blank=True, null=True)  # Field name made lowercase.
    # idbilling = models.ForeignKey(Billings, models.DO_NOTHING, db_column='IDBilling', blank=True, null=True)  # Field name made lowercase.
    # idpaymetrule = models.ForeignKey('Paymentrules', models.DO_NOTHING, db_column='IDPaymetRule', blank=True, null=True)  # Field name made lowercase.
    registredaddres = models.TextField(db_column='RegistredAddres', blank=True, null=True)  # Field name made lowercase.
    currentaddres = models.TextField(db_column='CurrentAddres', blank=True, null=True)  # Field name made lowercase.
    passport = models.TextField(db_column='Passport', blank=True, null=True)  # Field name made lowercase.
    license = models.TextField(db_column='License', blank=True, null=True)  # Field name made lowercase.
    licensedate = models.DateTimeField(db_column='LicenseDate', blank=True, null=True)  # Field name made lowercase.
    insurancedate = models.DateTimeField(db_column='InsuranceDate', blank=True, null=True)  # Field name made lowercase.
    failcounter = models.IntegerField(db_column='FailCounter', blank=True, null=True)  # Field name made lowercase.
    rating = models.IntegerField(db_column='Rating', blank=True, null=True)  # Field name made lowercase.
    iddefaultcar = models.ForeignKey(Cars, models.DO_NOTHING, db_column='IDDefaultCar', blank=True, null=True, related_name='iddefaultcar')  # Field name made lowercase.
    login = models.TextField(db_column='Login', blank=True, null=True)  # Field name made lowercase.
    password = models.TextField(db_column='Password', blank=True, null=True)  # Field name made lowercase.
    defaultcontacttype = models.BigIntegerField(db_column='DefaultContactType', blank=True, null=True)  # Field name made lowercase.
    ratingmodifier = models.IntegerField(db_column='RatingModifier', blank=True, null=True)  # Field name made lowercase.
    # idactiveplan = models.ForeignKey('Tariffsplans', models.DO_NOTHING, db_column='IDActivePlan', blank=True, null=True)  # Field name made lowercase.
    permissionnumber = models.CharField(db_column='PermissionNumber', max_length=30, blank=True, null=True)  # Field name made lowercase.
    isblocked = models.IntegerField(db_column='IsBlocked', blank=True, null=True)  # Field name made lowercase.
    # idblockreason = models.ForeignKey(Driverblockreasons, models.DO_NOTHING, db_column='IDBlockReason', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.IntegerField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    blockreasonstr = models.TextField(db_column='BlockReasonStr', blank=True, null=True)  # Field name made lowercase.
    blocker = models.TextField(db_column='Blocker', blank=True, null=True)  # Field name made lowercase.
    cancelassignmentcount = models.IntegerField(db_column='CancelAssignmentCount', blank=True, null=True)  # Field name made lowercase.
    cancelordercount = models.IntegerField(db_column='CancelOrderCount', blank=True, null=True)  # Field name made lowercase.
    paidordercount = models.IntegerField(db_column='PaidOrderCount', blank=True, null=True)  # Field name made lowercase.
    mincarpriority = models.IntegerField(db_column='MinCarPriority', blank=True, null=True)  # Field name made lowercase.
    maxcarpriority = models.IntegerField(db_column='MaxCarPriority', blank=True, null=True)  # Field name made lowercase.
    defaultgroupid = models.BigIntegerField(db_column='DefaultGroupID', blank=True, null=True)  # Field name made lowercase.
    assignnotconfirmcount = models.IntegerField(db_column='AssignNotConfirmCount', blank=True, null=True)  # Field name made lowercase.
    planningnotconfirmcount = models.IntegerField(db_column='PlanningNotConfirmCount', blank=True, null=True)  # Field name made lowercase.
    delaytoordercount = models.IntegerField(db_column='DelayToOrderCount', blank=True, null=True)  # Field name made lowercase.
    universalconditionhits = models.IntegerField(db_column='UniversalConditionHits', blank=True, null=True)  # Field name made lowercase.
    maxratingmodifier = models.IntegerField(db_column='MaxRatingModifier', blank=True, null=True)  # Field name made lowercase.
    minratingmodifier = models.IntegerField(db_column='MinRatingModifier', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    isnotcash = models.IntegerField(db_column='IsNotCash', blank=True, null=True)  # Field name made lowercase.
    realratingmodifier = models.IntegerField(db_column='RealRatingModifier', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Drivers'

    def __str__(self):
        return self.fullname


class TaOrders(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State')  # Field name made lowercase.
    idcar = models.BigIntegerField(db_column='IDCar', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime')  # Field name made lowercase.
    deliverytime = models.DateTimeField(db_column='DeliveryTime')  # Field name made lowercase.
    iddeliveryaddress = models.BigIntegerField(db_column='IDDeliveryAddress', blank=True, null=True)  # Field name made lowercase.
    idservice = models.BigIntegerField(db_column='IDService', blank=True, null=True)  # Field name made lowercase.
    cost = models.FloatField(db_column='Cost', blank=True, null=True)  # Field name made lowercase.
    ismanualcost = models.IntegerField(db_column='isManualCost', blank=True, null=True)  # Field name made lowercase.
    number = models.BigIntegerField(db_column='Number', blank=True, null=True)  # Field name made lowercase.
    acceptedbymodul = models.TextField(db_column='AcceptedByModul', blank=True, null=True)  # Field name made lowercase.
    isprevious = models.IntegerField(db_column='IsPrevious', blank=True, null=True)  # Field name made lowercase.
    predistance = models.FloatField(db_column='PreDistance', blank=True, null=True)  # Field name made lowercase.
    distance = models.FloatField(db_column='Distance', blank=True, null=True)  # Field name made lowercase.
    idclient = models.BigIntegerField(db_column='IDClient', blank=True, null=True)  # Field name made lowercase.
    phone = models.TextField(db_column='Phone', blank=True, null=True)  # Field name made lowercase.
    canclereason = models.TextField(db_column='CancleReason', blank=True, null=True)  # Field name made lowercase.
    timeofarrival = models.DateTimeField(db_column='TimeOfArrival', blank=True, null=True)  # Field name made lowercase.
    isnotcash = models.IntegerField(db_column='IsNotCash', blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='StartTime', blank=True, null=True)  # Field name made lowercase.
    isgiven = models.IntegerField(db_column='isGiven', blank=True, null=True)  # Field name made lowercase.
    assignbefore = models.DateTimeField(db_column='AssignBefore', blank=True, null=True)  # Field name made lowercase.
    idcontractor = models.BigIntegerField(db_column='IDContractor', blank=True, null=True)  # Field name made lowercase.
    command = models.IntegerField(db_column='Command', blank=True, null=True)  # Field name made lowercase.
    comproperty = models.BigIntegerField(db_column='ComProperty', blank=True, null=True)  # Field name made lowercase.
    autodistribution = models.IntegerField(db_column='AutoDistribution', blank=True, null=True)  # Field name made lowercase.
    innerid = models.TextField(db_column='InnerID', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    iddriver = models.BigIntegerField(db_column='IDDriver', blank=True, null=True)  # Field name made lowercase.
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    detailedcost = models.TextField(db_column='DetailedCost', blank=True, null=True)  # Field name made lowercase.
    entrance = models.CharField(db_column='Entrance', max_length=25, blank=True, null=True)  # Field name made lowercase.
    idcorporate = models.BigIntegerField(db_column='IDCorporate', blank=True, null=True)  # Field name made lowercase.
    idmaker = models.BigIntegerField(db_column='IDMaker', blank=True, null=True)  # Field name made lowercase.
    apartment = models.CharField(db_column='Apartment', max_length=25, blank=True, null=True)  # Field name made lowercase.
    deliverystr = models.CharField(db_column='DeliveryStr', max_length=250, blank=True, null=True)  # Field name made lowercase.
    destinationstr = models.TextField(db_column='DestinationStr', blank=True, null=True)  # Field name made lowercase.
    payfromdiscount = models.IntegerField(db_column='PayFromDiscount', blank=True, null=True)  # Field name made lowercase.
    iddiscountcard = models.BigIntegerField(db_column='IDDiscountCard', blank=True, null=True)  # Field name made lowercase.
    idroadsidetariff = models.BigIntegerField(db_column='IDRoadsideTariff', blank=True, null=True)  # Field name made lowercase.
    feedbackrating = models.IntegerField(db_column='FeedbackRating', blank=True, null=True)  # Field name made lowercase.
    feedbacknotes = models.TextField(db_column='FeedbackNotes', blank=True, null=True)  # Field name made lowercase.
    prevstate = models.IntegerField(db_column='PrevState', blank=True, null=True)  # Field name made lowercase.
    laststatetime = models.DateTimeField(db_column='LastStateTime', blank=True, null=True)  # Field name made lowercase.
    operatortype = models.IntegerField(db_column='OperatorType', blank=True, null=True)  # Field name made lowercase.
    idoperator = models.BigIntegerField(db_column='IDOperator', blank=True, null=True)  # Field name made lowercase.
    recallphone = models.TextField(db_column='RecallPhone', blank=True, null=True)  # Field name made lowercase.
    important = models.BigIntegerField(db_column='Important', blank=True, null=True)  # Field name made lowercase.
    filterdiscountbyclient = models.IntegerField(db_column='FilterDiscountByClient', blank=True, null=True)  # Field name made lowercase.
    paidfromdiscountsum = models.FloatField(db_column='PaidFromDiscountSum', blank=True, null=True)  # Field name made lowercase.
    setactivetime = models.DateTimeField(db_column='SetActiveTime', blank=True, null=True)  # Field name made lowercase.
    denynotify = models.IntegerField(db_column='DenyNotify', blank=True, null=True)  # Field name made lowercase.
    addrdescription = models.CharField(db_column='AddrDescription', max_length=100, blank=True, null=True)  # Field name made lowercase.
    destdescript = models.TextField(db_column='DestDescript', blank=True, null=True)  # Field name made lowercase.
    terminalinfo = models.TextField(db_column='TerminalInfo', blank=True, null=True)  # Field name made lowercase.
    idfastaddr = models.BigIntegerField(db_column='IDFastAddr', blank=True, null=True)  # Field name made lowercase.
    notifyresultwaiting = models.IntegerField(db_column='NotifyResultWaiting', blank=True, null=True)  # Field name made lowercase.
    notifyresultassigned = models.IntegerField(db_column='NotifyResultAssigned', blank=True, null=True)  # Field name made lowercase.
    notifyresultmoving = models.IntegerField(db_column='NotifyResultMoving', blank=True, null=True)  # Field name made lowercase.
    notifyresultrunning = models.IntegerField(db_column='NotifyResultRunning', blank=True, null=True)  # Field name made lowercase.
    notifyresultpaid = models.IntegerField(db_column='NotifyResultPaid', blank=True, null=True)  # Field name made lowercase.
    notifyresultunpaid = models.IntegerField(db_column='NotifyResultUnpaid', blank=True, null=True)  # Field name made lowercase.
    notifyresultcancelled = models.IntegerField(db_column='NotifyResultCancelled', blank=True, null=True)  # Field name made lowercase.
    iddeliveryzone = models.BigIntegerField(db_column='IDDeliveryZone', blank=True, null=True)  # Field name made lowercase.
    iddestinationzone = models.BigIntegerField(db_column='IDDestinationZone', blank=True, null=True)  # Field name made lowercase.
    copiescount = models.IntegerField(db_column='CopiesCount', blank=True, null=True)  # Field name made lowercase.
    idfinisher = models.BigIntegerField(db_column='IDFinisher', blank=True, null=True)  # Field name made lowercase.
    finishtime = models.DateTimeField(db_column='FinishTime', blank=True, null=True)  # Field name made lowercase.
    finishertype = models.IntegerField(db_column='FinisherType', blank=True, null=True)  # Field name made lowercase.
    iddispatcher = models.BigIntegerField(db_column='IDDispatcher', blank=True, null=True)  # Field name made lowercase.
    availableforreserve = models.IntegerField(db_column='AvailableForReserve', blank=True, null=True)  # Field name made lowercase.
    destinationzonestr = models.TextField(db_column='DestinationZoneStr', blank=True, null=True)  # Field name made lowercase.
    waitingstatenotifydonetime = models.DateTimeField(db_column='WaitingStateNotifyDoneTime', blank=True, null=True)  # Field name made lowercase.
    basecost = models.FloatField(db_column='BaseCost', blank=True, null=True)  # Field name made lowercase.
    yandexcanceltype = models.IntegerField(db_column='YandexCancelType', blank=True, null=True)  # Field name made lowercase.
    externalordertype = models.IntegerField(db_column='ExternalOrderType', blank=True, null=True)  # Field name made lowercase.
    releasetime = models.DateTimeField(db_column='ReleaseTime', blank=True, null=True)  # Field name made lowercase.
    yandexrequestdata = models.TextField(db_column='YandexRequestData', blank=True, null=True)  # Field name made lowercase.
    isreversed = models.IntegerField(db_column='IsReversed', blank=True, null=True)  # Field name made lowercase.
    idreverser = models.BigIntegerField(db_column='IDReverser', blank=True, null=True)  # Field name made lowercase.
    reversalreason = models.TextField(db_column='ReversalReason', blank=True, null=True)  # Field name made lowercase.
    ischecked = models.IntegerField(db_column='IsChecked', blank=True, null=True)  # Field name made lowercase.
    idchecker = models.BigIntegerField(db_column='IDChecker', blank=True, null=True)  # Field name made lowercase.
    idassigner = models.BigIntegerField(db_column='IDAssigner', blank=True, null=True)  # Field name made lowercase.
    reversalcomment = models.TextField(db_column='ReversalComment', blank=True, null=True)  # Field name made lowercase.
    groupaccess = models.TextField(db_column='GroupAccess', blank=True, null=True)  # Field name made lowercase.
    canceledby = models.IntegerField(db_column='CanceledBy', blank=True, null=True)  # Field name made lowercase.
    costcentre = models.TextField(db_column='CostCentre', blank=True, null=True)  # Field name made lowercase.
    contractnumber = models.TextField(db_column='ContractNumber', blank=True, null=True)  # Field name made lowercase.
    keyword = models.TextField(db_column='KeyWord', blank=True, null=True)  # Field name made lowercase.
    notifymethod = models.IntegerField(db_column='NotifyMethod', blank=True, null=True)  # Field name made lowercase.
    manualdistance = models.IntegerField(db_column='ManualDistance', blank=True, null=True)  # Field name made lowercase.
    payedwithcard = models.IntegerField(db_column='PayedWithCard', blank=True, null=True)  # Field name made lowercase.
    passengername = models.TextField(db_column='PassengerName', blank=True, null=True)  # Field name made lowercase.
    yandexwaitpaymentcomplete = models.IntegerField(db_column='YandexWaitPaymentComplete', blank=True, null=True)  # Field name made lowercase.
    yandexwarnnocard = models.IntegerField(db_column='YandexWarnNoCard', blank=True, null=True)  # Field name made lowercase.
    gpsturnedoff = models.IntegerField(db_column='GPSTurnedOff', blank=True, null=True)  # Field name made lowercase.
    invitation = models.IntegerField(db_column='Invitation', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TA_Orders'


class Parkings(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)  # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    orderview = models.IntegerField(db_column='OrderView', blank=True, null=True)  # Field name made lowercase.
    groupcaption = models.TextField(db_column='GroupCaption', blank=True, null=True)  # Field name made lowercase.
    carscount = models.IntegerField(db_column='CarsCount', blank=True, null=True)  # Field name made lowercase.
    orderscount = models.IntegerField(db_column='OrdersCount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Parkings'


class Colors(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Colors'


class Drivercontacts(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    idabonent = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='IDAbonent', blank=True, null=True)  # Field name made lowercase.
    idcontacttype = models.BigIntegerField(db_column='IDContactType')  # Field name made lowercase.
    contact = models.CharField(db_column='Contact', max_length=256, blank=True, null=True)  # Field name made lowercase.
    isdefault = models.IntegerField(db_column='IsDefault')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DriverContacts'


class TsOrders(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State')  # Field name made lowercase.
    idcar = models.BigIntegerField(db_column='IDCar', blank=True, null=True)  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime')  # Field name made lowercase.
    deliverytime = models.DateTimeField(db_column='DeliveryTime')  # Field name made lowercase.
    iddeliveryaddress = models.BigIntegerField(db_column='IDDeliveryAddress', blank=True, null=True)  # Field name made lowercase.
    idservice = models.BigIntegerField(db_column='IDService', blank=True, null=True)  # Field name made lowercase.
    cost = models.FloatField(db_column='Cost', blank=True, null=True)  # Field name made lowercase.
    ismanualcost = models.IntegerField(db_column='isManualCost', blank=True, null=True)  # Field name made lowercase.
    number = models.BigIntegerField(db_column='Number', blank=True, null=True)  # Field name made lowercase.
    acceptedbymodul = models.TextField(db_column='AcceptedByModul', blank=True, null=True)  # Field name made lowercase.
    isprevious = models.IntegerField(db_column='IsPrevious', blank=True, null=True)  # Field name made lowercase.
    predistance = models.FloatField(db_column='PreDistance', blank=True, null=True)  # Field name made lowercase.
    distance = models.FloatField(db_column='Distance', blank=True, null=True)  # Field name made lowercase.
    idclient = models.BigIntegerField(db_column='IDClient', blank=True, null=True)  # Field name made lowercase.
    phone = models.TextField(db_column='Phone', blank=True, null=True)  # Field name made lowercase.
    canclereason = models.TextField(db_column='CancleReason', blank=True, null=True)  # Field name made lowercase.
    timeofarrival = models.DateTimeField(db_column='TimeOfArrival', blank=True, null=True)  # Field name made lowercase.
    isnotcash = models.IntegerField(db_column='IsNotCash', blank=True, null=True)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='StartTime', blank=True, null=True)  # Field name made lowercase.
    isgiven = models.IntegerField(db_column='isGiven', blank=True, null=True)  # Field name made lowercase.
    assignbefore = models.DateTimeField(db_column='AssignBefore', blank=True, null=True)  # Field name made lowercase.
    idcontractor = models.BigIntegerField(db_column='IDContractor', blank=True, null=True)  # Field name made lowercase.
    command = models.IntegerField(db_column='Command', blank=True, null=True)  # Field name made lowercase.
    comproperty = models.BigIntegerField(db_column='ComProperty', blank=True, null=True)  # Field name made lowercase.
    autodistribution = models.IntegerField(db_column='AutoDistribution', blank=True, null=True)  # Field name made lowercase.
    innerid = models.TextField(db_column='InnerID', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    iddriver = models.BigIntegerField(db_column='IDDriver', blank=True, null=True)  # Field name made lowercase.
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    detailedcost = models.TextField(db_column='DetailedCost', blank=True, null=True)  # Field name made lowercase.
    entrance = models.CharField(db_column='Entrance', max_length=25, blank=True, null=True)  # Field name made lowercase.
    idcorporate = models.BigIntegerField(db_column='IDCorporate', blank=True, null=True)  # Field name made lowercase.
    idmaker = models.BigIntegerField(db_column='IDMaker', blank=True, null=True)  # Field name made lowercase.
    apartment = models.CharField(db_column='Apartment', max_length=25, blank=True, null=True)  # Field name made lowercase.
    deliverystr = models.CharField(db_column='DeliveryStr', max_length=250, blank=True, null=True)  # Field name made lowercase.
    destinationstr = models.TextField(db_column='DestinationStr', blank=True, null=True)  # Field name made lowercase.
    payfromdiscount = models.IntegerField(db_column='PayFromDiscount', blank=True, null=True)  # Field name made lowercase.
    iddiscountcard = models.BigIntegerField(db_column='IDDiscountCard', blank=True, null=True)  # Field name made lowercase.
    idroadsidetariff = models.BigIntegerField(db_column='IDRoadsideTariff', blank=True, null=True)  # Field name made lowercase.
    deletedfromclientterminal = models.IntegerField(db_column='DeletedFromClientTerminal', blank=True, null=True)  # Field name made lowercase.
    feedbackrating = models.IntegerField(db_column='FeedbackRating', blank=True, null=True)  # Field name made lowercase.
    feedbacknotes = models.TextField(db_column='FeedbackNotes', blank=True, null=True)  # Field name made lowercase.
    prevstate = models.IntegerField(db_column='PrevState', blank=True, null=True)  # Field name made lowercase.
    laststatetime = models.DateTimeField(db_column='LastStateTime', blank=True, null=True)  # Field name made lowercase.
    operatortype = models.IntegerField(db_column='OperatorType', blank=True, null=True)  # Field name made lowercase.
    idoperator = models.BigIntegerField(db_column='IDOperator', blank=True, null=True)  # Field name made lowercase.
    recallphone = models.TextField(db_column='RecallPhone', blank=True, null=True)  # Field name made lowercase.
    important = models.BigIntegerField(db_column='Important', blank=True, null=True)  # Field name made lowercase.
    filterdiscountbyclient = models.IntegerField(db_column='FilterDiscountByClient', blank=True, null=True)  # Field name made lowercase.
    paidfromdiscountsum = models.FloatField(db_column='PaidFromDiscountSum', blank=True, null=True)  # Field name made lowercase.
    setactivetime = models.DateTimeField(db_column='SetActiveTime', blank=True, null=True)  # Field name made lowercase.
    denynotify = models.IntegerField(db_column='DenyNotify', blank=True, null=True)  # Field name made lowercase.
    addrdescription = models.CharField(db_column='AddrDescription', max_length=100, blank=True, null=True)  # Field name made lowercase.
    destdescript = models.TextField(db_column='DestDescript', blank=True, null=True)  # Field name made lowercase.
    terminalinfo = models.TextField(db_column='TerminalInfo', blank=True, null=True)  # Field name made lowercase.
    idfastaddr = models.BigIntegerField(db_column='IDFastAddr', blank=True, null=True)  # Field name made lowercase.
    notifyresultwaiting = models.IntegerField(db_column='NotifyResultWaiting', blank=True, null=True)  # Field name made lowercase.
    notifyresultassigned = models.IntegerField(db_column='NotifyResultAssigned', blank=True, null=True)  # Field name made lowercase.
    notifyresultmoving = models.IntegerField(db_column='NotifyResultMoving', blank=True, null=True)  # Field name made lowercase.
    notifyresultrunning = models.IntegerField(db_column='NotifyResultRunning', blank=True, null=True)  # Field name made lowercase.
    notifyresultpaid = models.IntegerField(db_column='NotifyResultPaid', blank=True, null=True)  # Field name made lowercase.
    notifyresultunpaid = models.IntegerField(db_column='NotifyResultUnpaid', blank=True, null=True)  # Field name made lowercase.
    notifyresultcancelled = models.IntegerField(db_column='NotifyResultCancelled', blank=True, null=True)  # Field name made lowercase.
    iddeliveryzone = models.BigIntegerField(db_column='IDDeliveryZone', blank=True, null=True)  # Field name made lowercase.
    iddestinationzone = models.BigIntegerField(db_column='IDDestinationZone', blank=True, null=True)  # Field name made lowercase.
    copiescount = models.IntegerField(db_column='CopiesCount', blank=True, null=True)  # Field name made lowercase.
    finishtime = models.DateTimeField(db_column='FinishTime', blank=True, null=True)  # Field name made lowercase.
    idfinisher = models.BigIntegerField(db_column='IDFinisher', blank=True, null=True)  # Field name made lowercase.
    finishertype = models.IntegerField(db_column='FinisherType', blank=True, null=True)  # Field name made lowercase.
    iddispatcher = models.BigIntegerField(db_column='IDDispatcher', blank=True, null=True)  # Field name made lowercase.
    availableforreserve = models.IntegerField(db_column='AvailableForReserve', blank=True, null=True)  # Field name made lowercase.
    destinationzonestr = models.TextField(db_column='DestinationZoneStr', blank=True, null=True)  # Field name made lowercase.
    waitingstatenotifydonetime = models.DateTimeField(db_column='WaitingStateNotifyDoneTime', blank=True, null=True)  # Field name made lowercase.
    basecost = models.FloatField(db_column='BaseCost', blank=True, null=True)  # Field name made lowercase.
    yandexcanceltype = models.IntegerField(db_column='YandexCancelType', blank=True, null=True)  # Field name made lowercase.
    externalordertype = models.IntegerField(db_column='ExternalOrderType', blank=True, null=True)  # Field name made lowercase.
    releasetime = models.DateTimeField(db_column='ReleaseTime', blank=True, null=True)  # Field name made lowercase.
    yandexrequestdata = models.TextField(db_column='YandexRequestData', blank=True, null=True)  # Field name made lowercase.
    ischecked = models.IntegerField(db_column='IsChecked', blank=True, null=True)  # Field name made lowercase.
    isreversed = models.IntegerField(db_column='IsReversed', blank=True, null=True)  # Field name made lowercase.
    idreverser = models.BigIntegerField(db_column='IDReverser', blank=True, null=True)  # Field name made lowercase.
    reversalreason = models.TextField(db_column='ReversalReason', blank=True, null=True)  # Field name made lowercase.
    idchecker = models.BigIntegerField(db_column='IDChecker', blank=True, null=True)  # Field name made lowercase.
    idassigner = models.BigIntegerField(db_column='IDAssigner', blank=True, null=True)  # Field name made lowercase.
    reversalcomment = models.TextField(db_column='ReversalComment', blank=True, null=True)  # Field name made lowercase.
    groupaccess = models.TextField(db_column='GroupAccess', blank=True, null=True)  # Field name made lowercase.
    canceledby = models.IntegerField(db_column='CanceledBy', blank=True, null=True)  # Field name made lowercase.
    costcentre = models.TextField(db_column='CostCentre', blank=True, null=True)  # Field name made lowercase.
    contractnumber = models.TextField(db_column='ContractNumber', blank=True, null=True)  # Field name made lowercase.
    keyword = models.TextField(db_column='KeyWord', blank=True, null=True)  # Field name made lowercase.
    notifymethod = models.IntegerField(db_column='NotifyMethod', blank=True, null=True)  # Field name made lowercase.
    manualdistance = models.IntegerField(db_column='ManualDistance', blank=True, null=True)  # Field name made lowercase.
    payedwithcard = models.IntegerField(db_column='PayedWithCard', blank=True, null=True)  # Field name made lowercase.
    passengername = models.TextField(db_column='PassengerName', blank=True, null=True)  # Field name made lowercase.
    yandexwaitpaymentcomplete = models.IntegerField(db_column='YandexWaitPaymentComplete', blank=True, null=True)  # Field name made lowercase.
    yandexwarnnocard = models.IntegerField(db_column='YandexWarnNoCard', blank=True, null=True)  # Field name made lowercase.
    gpsturnedoff = models.IntegerField(db_column='GPSTurnedOff', blank=True, null=True)  # Field name made lowercase.
    invitation = models.IntegerField(db_column='Invitation', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TS_Orders'

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.iddriver)
        return driver.fullname

    def get_corporate_name(self):
        corporate = Corporations.objects.using('Cx_TaxiConfiguration').get(id=self.idcorporate)
        return corporate.name


class TsCarstatechanges(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    idcar = models.BigIntegerField(db_column='IDCar', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    operatortype = models.IntegerField(db_column='OperatorType', blank=True, null=True)  # Field name made lowercase.
    iddriver = models.BigIntegerField(db_column='IDDriver', blank=True, null=True)  # Field name made lowercase.
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    terminaltype = models.IntegerField(db_column='TerminalType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TS_CarStateChanges'


class Clientcontacts(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    idabonent = models.ForeignKey('Clients', models.DO_NOTHING, db_column='IDAbonent', blank=True, null=True)  # Field name made lowercase.
    idcontacttype = models.BigIntegerField(db_column='IDContactType')  # Field name made lowercase.
    contact = models.CharField(db_column='Contact', max_length=256, blank=True, null=True)  # Field name made lowercase.
    isdefault = models.IntegerField(db_column='IsDefault')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ClientContacts'


class Clients(models.Model):
    id = models.BigIntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    # idbilling = models.ForeignKey(Billings, models.DO_NOTHING, db_column='IDBilling', blank=True, null=True)  # Field name made lowercase.
    orderscounter = models.IntegerField(db_column='OrdersCounter', blank=True, null=True)  # Field name made lowercase.
    orderscanceled = models.IntegerField(db_column='OrdersCanceled', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    # iddefaultservice = models.ForeignKey('Services', models.DO_NOTHING, db_column='IDDefaultService', blank=True, null=True)  # Field name made lowercase.
    iddeliveriadds = models.BigIntegerField(db_column='IDDeliveriAdds', blank=True, null=True)  # Field name made lowercase.
    iddestionationadds = models.BigIntegerField(db_column='IDDestionationAdds', blank=True, null=True)  # Field name made lowercase.
    idcorporation = models.BigIntegerField(db_column='IDCorporation', blank=True, null=True)  # Field name made lowercase.
    entrance = models.CharField(db_column='Entrance', max_length=25, blank=True, null=True)  # Field name made lowercase.
    login = models.TextField(db_column='Login', blank=True, null=True)  # Field name made lowercase.
    password = models.TextField(db_column='Password', blank=True, null=True)  # Field name made lowercase.
    cantrun = models.IntegerField(db_column='CantRun', blank=True, null=True)  # Field name made lowercase.
    apartment = models.CharField(db_column='Apartment', max_length=25, blank=True, null=True)  # Field name made lowercase.
    cashless = models.IntegerField(db_column='Cashless', blank=True, null=True)  # Field name made lowercase.
    # iddefaultdiscount = models.ForeignKey('Discountcards', models.DO_NOTHING, db_column='IDDefaultDiscount', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    # idlanguage = models.ForeignKey('Translationlanguages', models.DO_NOTHING, db_column='IDLanguage', blank=True, null=True)  # Field name made lowercase.
    birthday = models.DateTimeField(db_column='Birthday', blank=True, null=True)  # Field name made lowercase.
    rating = models.FloatField(db_column='Rating', blank=True, null=True)  # Field name made lowercase.
    guid = models.TextField(db_column='GUID', blank=True, null=True)  # Field name made lowercase.
    addrdescription = models.TextField(db_column='AddrDescription', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Clients'
