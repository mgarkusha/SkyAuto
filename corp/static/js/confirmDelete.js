function confirmDelete(complaint_number, complaint_date) {
	if (confirm("Вы подтверждаете удаление жалобы № " + complaint_number + " от " + complaint_date + " ?")) {
		return true;
	} else {
		return false;
	}
}

function confirmDeleteSmena(smena_number, smena_date) {
	if (confirm("Вы подтверждаете удаление смены № " + smena_number + " от " + smena_date + " ?")) {
		return true;
	} else {
		return false;
	}
}

function confirmDeletePayment(payment_sum, payment_date) {
	if (confirm("Вы подтверждаете удаление платежа на сумму " + payment_sum + " от " + payment_date + " ?")) {
		return true;
	} else {
		return false;
	}
}

function confirmDeleteGibdd(gibdd_id, gibdd_date) {
	if (confirm("Вы подтверждаете удаление штрафа № " + gibdd_id + " от " + gibdd_date + " ?")) {
		return true;
	} else {
		return false;
	}
}


function confirmDeleteCompanyPenalty(company_penalty_id, company_penalty_date) {
	if (confirm("Вы подтверждаете удаление штрафа компании № " + company_penalty_id + " от " + company_penalty_date + " ?")) {
		return true;
	} else {
		return false;
	}
}


function confirmDeleteWashOrder(car_num, order_date) {
	if (confirm("Вы подтверждаете удаление мойки АВТО № " + car_num + " от " + order_date + " ?")) {
		return true;
	} else {
		return false;
	}
}