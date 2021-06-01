import os
import optparse
from datetime import datetime


def main():
    parser = optparse.OptionParser()
    parser.add_option("--SourceDir", dest="src_dir",
                      help="Configuration file")
    parser.add_option("--DestDir", dest="dest_dir",
                      help="")
    parser.add_option("--StartDate", dest="start_date",
                      help="")
    parser.add_option("--EndDate", dest="end_date",
                      help="")

    (options, args) = parser.parse_args()


    files = os.listdir(options.src_dir)

    start_date = datetime.strptime(options.start_date, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(options.end_date, '%Y-%m-%d %H:%M:%S')
    for src_file in files:
        outfile = os.path.join(options.dest_dir, src_file)
        infile = os.path.join(options.src_dir, src_file)
        print("Opening source: %s" % (infile))
        with open(infile, 'r', newline='\r\n') as input_file:
            print("Opening dest: %s" % (outfile))
            with open(outfile, 'w', newline='\r\n') as output_file:
                row_cnt = 0
                read_src = True
                header_row = ''
                while read_src:
                    if row_cnt == 0:
                        header_row = input_file.readline()
                        output_file.writelines(header_row)
                    else:
                        data_row = input_file.readline()
                        if len(data_row):
                            cols = data_row.split(',')
                            row_date = '%s %s' % (cols[0], cols[1])
                            row_date = datetime.strptime(row_date, '%m/%d/%Y %H:%M:%S')
                            #Determine if row is inbetween dates.
                            if row_date >= start_date and row_date < end_date:
                                output_file.writelines(data_row)
                        else:
                            read_src = False
                    row_cnt += 1



    return

if __name__ == "__main__":
    main()
