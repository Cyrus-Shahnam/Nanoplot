#BEGIN_HEADER
import logging
import os
import subprocess
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
#END_HEADER

class acshahnam_nanoplot:
    '''
    Module Name:
    acshahnam_nanoplot

    Module Description:
    A KBase module that runs NanoPlot on SingleEndLibrary FASTQ reads and generates a report.
    '''

    VERSION = "0.0.1"
    GIT_URL = "https://github.com/your_username/acshahnam_nanoplot"
    GIT_COMMIT_HASH = "REPLACE_WITH_ACTUAL_COMMIT_HASH"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

        def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.dfu = DataFileUtil(self.callback_url)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
    #END_CONSTRUCTOR

    #BEGIN run_acshahnam_nanoplot
    def run_acshahnam_nanoplot(self, ctx, params):
        logging.info("Starting NanoPlot run")
        
        # Download reads
        reads_ref = params['reads_input_ref']
        logging.info(f"Fetching reads: {reads_ref}")

        reads_info = self.dfu.download_reads({
            'read_libraries': [reads_ref],
            'interleaved': False,
            'gzipped': True
        })

        fastq_path = reads_info['files'][reads_ref]['files']['fwd']
        logging.info(f"Downloaded FASTQ file to: {fastq_path}")

        # Set up output directory
        output_dir = os.path.join(self.scratch, "nanoplot_output")
        os.makedirs(output_dir, exist_ok=True)

        # Run NanoPlot
        cmd = [
            'NanoPlot',
            '--fastq', fastq_path,
            '--outdir', output_dir,
            '--plots', 'kde',
            '--N50'
        ]

        logging.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        # Find HTML report
        html_report_path = os.path.join(output_dir, "NanoPlot-report.html")
        if not os.path.exists(html_report_path):
            raise FileNotFoundError("NanoPlot report not found.")

        # Copy to scratch root for upload
        copied_html_path = os.path.join(self.scratch, "NanoPlot-report.html")
        os.rename(html_report_path, copied_html_path)

        # Generate report
        report_client = KBaseReport(self.callback_url)
        report_info = report_client.create_extended_report({
            'direct_html_link_index': 0,
            'html_links': [{
                'name': 'NanoPlot-report.html',
                'path': copied_html_path
            }],
            'report_object_name': 'nanoplot_report',
            'workspace_name': params['workspace_name']
        })

        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }

        return output
    #END run_acshahnam_nanoplot

    def status(self):
    #BEGIN_STATUS
        return {
            'state': "OK",
            'message': "",
            'version': self.VERSION,
            'git_url': self.GIT_URL,
            'git_commit_hash': self.GIT_COMMIT_HASH
        }
    #END_STATUS
