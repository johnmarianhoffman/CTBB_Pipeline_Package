from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='CTBB_Pipeline',
      version='0.1',
      description='Pipelinize that CTBangBang',
      url='http://github.com/captnjohnny1618/CTBB_Pipeline_Package',
      author='John Hoffman',
      author_email='captnjohnny1618@gmail.com',
      license='GNU GPL v2.0',
      packages=['CTBB_Pipeline'],
      include_package_data=True,
      install_requires=[
          "numpy",
          "pyyaml",
          "jinja2",
          "pyqtgraph",
          "pycuda",
          "xmltodict",
          ],
      scripts=[
          "bin/ctbb_copy_pipeline_dataset",          
          "bin/ctbb_pipeline_daemon",
          "bin/ctbb_pipeline_diff",
          "bin/ctbb_pipeline_kill",
          "bin/ctbb_pipeline_launch",
          "bin/ctbb_pipeline_metrics",
          "bin/ctbb_pipeline.py",
          "bin/ctbb_pipeline_qa_docs",
          "bin/ctbb_queue_item",
          "bin/ctbb_q",
      ],
      data_files=[
          "CTBB_Pipeline/data/ctbb_pipeline.ui",
          "CTBB_Pipeline/data/qa_template.tpl",          
      ],
      zip_safe=False)

