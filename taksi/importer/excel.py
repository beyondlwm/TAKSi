# Copyright (C) 2018-present prototyped.cn. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.

import os
import unittest
import taksi.descriptor.types as types
import taksi.descriptor.predef as predef
import taksi.descriptor.strutil as strutil
import taksi.importer.xlsxwrap as xlsxwrap


# excel导入
class ExcelImporter:

    def __init__(self):
        self.options = []
        self.filenames = []
        self.meta = {}

    @staticmethod
    def name():
        return "excel"

    def initialize(self, args):
        self.options = args
        self.make_filenames()

    # 从路径种搜索所有excel文件
    def enum_files(self, rootdir):
        files = []
        for dirpath, dirnames, filenames in os.walk(rootdir):
            for filename in filenames:
                 if filename.endswith(".xlsx"):
                     files.append(dirpath + os.sep + filename)
        filenames = []
        for filename in files:
            if not xlsxwrap.is_ignored_filename(filename):
                filename = os.path.abspath(filename)
                filenames.append(filename)
        return filenames

    # 跳过忽略的文件名
    def make_filenames(self):
        filenames = []
        filename = self.options[predef.PredefFilenameOption]
        assert os.path.exists(filename), '%s not exist' % filename
        if os.path.isdir(filename):    # filename is a directory
            print('parse files in directory:', filename)
            filenames = self.enum_files(filename)
        else:
            assert os.path.isfile(filename)
            filename = os.path.abspath(filename)
            filenames.append(filename)

        skip_names = []
        if self.options.get(predef.PredefSkipFileOption, "") != "":
            skip_names = self.options[predef.PredefSkipFileOption].split(' ')

        print('skipped names', skip_names)
        for filename in filenames:
            ignored = False
            for skip_name in skip_names:
                skip_name = skip_name.strip()
                if len(skip_name) > 0:
                    if filename.find(skip_name) >= 0:
                        ignored = True
            if not ignored:
                self.filenames.append(filename)

    # 解析excel表中的meta sheet
    def parse_meta_sheet(self, sheet_rows):
        meta = {}
        for row in sheet_rows:
            if len(row) >= 2:
                key = row[0].strip()
                value = row[1].strip()
                if key != "" and value != "":
                    meta[key] = value

        # default values
        if predef.PredefStructTypeRow not in meta:
            meta[predef.PredefStructTypeRow] = "1"  # 类型列
        if predef.PredefStructNameRow not in meta:
            meta[predef.PredefStructNameRow] = "2"  # 名称列
        if predef.PredefCommentRow not in meta:
            meta[predef.PredefCommentRow] = "3"     # 注释列
        if predef.PredefDataStartRow not in meta:
            meta[predef.PredefDataStartRow] = "4"   # 数据起始列

        self.meta = meta

    # 解析数据列
    def parse_data_sheet(self, rows):
        assert len(rows) > 0

        # validate meta index
        type_index = int(self.meta[predef.PredefStructTypeRow])
        assert type_index < len(rows), type_index
        name_index = int(self.meta[predef.PredefStructNameRow])
        assert name_index < len(rows), name_index
        data_start_index = int(self.meta[predef.PredefDataStartRow])
        data_end_index = len(rows)
        if predef.PredefDataEndRow in self.meta:
            data_end_index = int(self.meta[predef.PredefDataEndRow])
            assert data_end_index <= len(rows), data_end_index
        assert data_start_index < len(rows), data_start_index
        assert data_start_index <= data_end_index, data_end_index

        struct = {}
        struct['fields'] = []

        struct['comment'] = self.meta.get(predef.PredefClassComment, "")

        class_name = self.meta[predef.PredefClassName]
        assert len(class_name) > 0
        struct['name'] = class_name
        struct['camel_case_name'] = strutil.camel_case(class_name)

        comment_index = -1
        if predef.PredefCommentRow in self.meta:
            index = int(self.meta[predef.PredefCommentRow])
            if index > 0:
                comment_index = index - 1   # to zero-based

        type_row = rows[type_index - 1]
        name_row = rows[name_index - 1]
        fields_names = {}
        prev_field = None
        for i in range(len(type_row)):
            if type_row[i] == "" or name_row[i] == "":  # skip empty column
                continue
            field = {}
            field["name"] = name_row[i]
            field["camel_case_name"] = strutil.camel_case(name_row[i])
            field["original_type_name"] = type_row[i]
            field["type"] = types.get_type_by_name(type_row[i])
            field["type_name"] = types.get_name_of_type(field["type"])
            field["column_index"] = i + 1

            assert field["name"] not in fields_names, field["name"]
            fields_names[field["name"]] = True

            if prev_field is not None:
                is_vector = strutil.is_vector_fields(prev_field, field)
                # print('is vector', is_vector, prev_field, field)
                if is_vector:
                    prev_field["is_vector"] = True
                    field["is_vector"] = True
            prev_field = field

            assert field["type"] != types.Type_Unknown
            assert field["type_name"] != ""

            field["comment"] = " "
            if comment_index > 0:
                field["comment"] = rows[comment_index][i]

            # print(field)
            struct['fields'].append(field)

        data_rows = rows[data_start_index - 1: data_end_index]
        data_rows = self.pad_data_rows(data_rows, struct)
        data_rows = xlsxwrap.validate_data_rows(data_rows, struct)
        struct["options"] = self.meta
        struct["data_rows"] = data_rows

        return struct

    # 对齐数据行
    def pad_data_rows(self, rows, struct):
        # pad empty row
        max_row_len = len(struct['fields'])
        for row in rows:
            if len(row) > max_row_len:
                max_row_len = len(row)

        for i in range(len(row)):
            for j in range(len(row), max_row_len):
                rows[i].append("")

        # 删除未导出的列
        new_rows = []
        fields = sorted(struct['fields'], key=lambda fld: fld['column_index'])
        for row in rows:
            new_row = []
            for field in fields:
                new_row.append(row[field['column_index']-1])
            new_rows.append(new_row)
        return new_rows

    # 导入所有
    def import_all(self):
        descriptors = []
        for filename in self.filenames:
            print(strutil.current_time(), "start parse", filename)
            descriptor = self.import_one(filename)
            if descriptor is not None:
                descriptor['source'] = filename
                descriptors.append(descriptor)
        return descriptors

    # 导入单个文件
    def import_one(self, filename):
        wb, sheet_names = xlsxwrap.read_workbook_and_sheet_names(filename)
        sheet_names = wb.sheetnames
        assert len(sheet_names) > 0
        if predef.PredefMetaSheet not in sheet_names:
            print('%s, no meta sheet found' % filename, 'red')
            xlsxwrap.close_workbook(wb)
        else:
            # parse meta sheet
            sheet_data = xlsxwrap.read_workbook_sheet_to_rows(wb, predef.PredefMetaSheet)
            self.parse_meta_sheet(sheet_data)

            # default parse first sheet
            sheet_data = xlsxwrap.read_workbook_sheet_to_rows(wb, sheet_names[0])
            xlsxwrap.close_workbook(wb)

            struct = self.parse_data_sheet(sheet_data)
            struct['file'] = os.path.basename(filename)
            return struct


class TestExcelImporter(unittest.TestCase):

    def test_enum_file(self):
        filename = u'''新建筑.xlsx'''
        importer = ExcelImporter()
        importer.initialize('file=%s' % filename)
        all = importer.import_all()
        print(strutil.current_time(), 'done')
        assert len(all) > 0
        for struct in all:
            print(struct)


if __name__ == '__main__':
    unittest.main()
