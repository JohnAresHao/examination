# -*- coding: utf-8 -*-

import xlrd

from django.db import transaction

from competition.models import ChoiceInfo, FillInBlankInfo


def check_vals(val):
    val = str(val)
    if val.endswith('.0'):
        val = val[:-2]
    return val


@transaction.atomic
def upload_questions(file_path=None, bank_info=None):
    book = xlrd.open_workbook(file_path)
    table = book.sheets()[0]
    nrows = table.nrows
    choice_num = 0
    fillinblank_num = 0

    for i in range(1, nrows):
        rvalues = table.row_values(i)
        if (not rvalues[0]) or rvalues[0].startswith('说明'):
            break

        if '##' in rvalues[0]:
            FillInBlankInfo.objects.select_for_update().create(
                bank_id=bank_info.bank_id,
                question=check_vals(rvalues[0]),
                answer=check_vals(rvalues[1]),
                image_url=rvalues[6],
                source=rvalues[7]
            )
            fillinblank_num += 1

        else:
            ChoiceInfo.objects.select_for_update().create(
                bank_id=bank_info.bank_id,
                question=check_vals(rvalues[0]),
                answer=check_vals(rvalues[1]),
                item1=check_vals(rvalues[2]),
                item2=check_vals(rvalues[3]),
                item3=check_vals(rvalues[4]),
                item4=check_vals(rvalues[5]),
                image_url=rvalues[6],
                source=rvalues[7]
            )
            choice_num += 1

    bank_info.choice_num = choice_num
    bank_info.fillinblank_num = fillinblank_num
    bank_info.save()

    return choice_num, fillinblank_num
